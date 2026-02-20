import pyvirtualcam
import cv2
import sys
import queue
import time
import signal
import logging
import threading

from conf import *
from shared import *
from control_window import *
from plugins.pong import PongRenderPass
from plugins.rain import RandomFlashRenderPass
from plugins.static_text import StaticTextRenderPass
from plugins.shell_watch import ShellWatcherRenderPass
from plugins.typing_text import TypingTextRenderPass
from plugins.shape_detection import CarDrawRenderPass
from plugins.dot_detection import RedDotDrawRenderPass
from plugins.template_detection import TemplateRecognitionDrawRenderPass
from plugins.mouse_drawing import MouseDrawRenderPass
from plugins.morse_code import MorseCodeRenderPass
from plugins.timer import TimerRenderPass


logging.basicConfig()
logging.root.setLevel(logging.NOTSET)
logging.basicConfig(level=logging.NOTSET)


def sig_interrupt_handler(sig, frame):
    global global_exit_flag
    logging.info("Waiting for processes to finish")

    global_exit_flag = True

    time.sleep(1)
    logging.info("Exiting Video Proxy")

    sys.exit(0)


def window_thread(
    event_queue: queue.Queue, output_render_passes: list[OutputRenderPass]
):
    ControlWindow(event_queue, output_render_passes).run()


def start_window_thread(
    event_queue: queue.Queue, output_render_passes: list[OutputRenderPass]
) -> threading.Thread:
    thread = threading.Thread(
        target=window_thread,
        args=(
            event_queue,
            output_render_passes,
        ),
    )
    thread.daemon = True
    thread.start()

    return thread


#
# Environment config collecting all env and command line args used in the app.
#
class EnvConfig:
    def __init__(self):
        self.raw_args = sys.argv
        self.value_args = {}
        self.flags = []

        for raw_arg in self.raw_args:
            if raw_arg.find("=") > 0:
                parts = raw_arg.split("=")
                self.value_args[parts[0]] = parts[1]
            else:
                self.flags.append(raw_arg)


class VideoProxy:
    def __init__(self, env_config: EnvConfig, fps):
        logging.info("Video Proxy start")

        self.event_queue: queue.Queue[Event] = queue.Queue()
        self.env_config = env_config
        self.config = Config()

        self.fps_value = fps
        self.width = OUT_WIDTH
        self.height = OUT_HEIGHT

        self.output_rect = (self.width, self.height)

        self.videoInputOriginal = cv2.VideoCapture(IN_VIDEO_DEVICE_ID)

        self.output_render_passes = [
            StaticTextRenderPass("Video Proxy Demo v0.2"),
            RandomFlashRenderPass(),
            TypingTextRenderPass(),
            MorseCodeRenderPass(),
            PongRenderPass(),
            ShellWatcherRenderPass(["vmstat"], 30, 10, 30),
            ShellWatcherRenderPass(["cat", "./README.md"], 30, 10, 30),
            MouseDrawRenderPass(),
            TimerRenderPass(),
            RedDotDrawRenderPass(LineDrawer()),
            TemplateRecognitionDrawRenderPass(),
            CarDrawRenderPass(),
        ]
        for i, render_pass in enumerate(self.output_render_passes):
            logging.info("Pass #" + str(i) + ": " + render_pass.name())

        self.window_thread = start_window_thread(
            self.event_queue, self.output_render_passes
        )

    def img_size(self):
        return self.output_rect

    def fps(self):
        return self.fps_value

    def run(self):
        global global_exit_flag
        global background

        output_render_pass_toggles = [False] * len(self.output_render_passes)
        is_pip_mode = False

        with pyvirtualcam.Camera(
            width=OUT_WIDTH, height=OUT_HEIGHT, fps=OUT_FPS
        ) as cam:
            logging.info(f"Using virtual camera: {cam.device}")

            while not global_exit_flag:
                # Read the system default (0) video stream frame.
                rval, default_video = self.videoInputOriginal.read()
                if not rval:
                    logging.error("Failed retrieving default video stream frame")
                    global_exit_flag = True
                    break

                # In PIP mode the default video is presented small in the top right corner.
                if is_pip_mode:
                    default_video_resized = cv2.resize(
                        default_video, (self.width >> 2, self.height >> 2)
                    )
                    img = background.copy()
                    img[0 : (self.height >> 2), 0 : (self.width >> 2)] = (
                        default_video_resized
                    )
                else:
                    img = cv2.resize(default_video, (self.width, self.height))

                # Move out accumulated UI events from the thread safe queue.
                events = []
                while self.event_queue.qsize() > 0:
                    event = self.event_queue.get()
                    events.append(event)

                    if event.kind() == EVENT_KIND_TOGGLE_RENDER_PASS:
                        output_render_pass_toggles[event.data.render_pass_index] = (
                            event.data.is_on
                        )

                # Execute render passes.
                for i, output_render_pass in enumerate(self.output_render_passes):
                    if output_render_pass_toggles[i]:
                        img = output_render_pass.render(img, events, self.config)

                img = cv2.flip(img, 1)
                cam.send(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                cam.sleep_until_next_frame()

            self.window_thread.join()


# CTRL-C handler.
signal.signal(signal.SIGINT, sig_interrupt_handler)

config = EnvConfig()
fps = config.value_args.get(ARG_FPS) or OUT_FPS

vp = VideoProxy(config, fps)
vp.run()
