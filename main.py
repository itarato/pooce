"""
Pooce - A Python video proxy

Pooce is an artificial video output stream that allows interaction (plugins).
It works in a very simple way: it opens a video device and puts a renderable frame onto the output. This frame
is a copy of the default available video device (existing webcam).
The output is handed over to a list of programmable passes (output render passes) before the
final return.

Currently only supported on Linux.
"""

import virtualvideo
import cv2
import select
import sys
import numpy
import threading
import queue
import time
import signal
import logging

from conf import *
from shared import *
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


#
# App level control window for event collection (mouse and keyboard).
#
class ControlWindow:
    def __init__(self, event_queue: queue.Queue):
        self.window_name = "pooce-mouse"
        self.event_queue = event_queue
        threading.Thread(target=self.window_thread).start()

    def window_thread(self):
        global global_exit_flag
        global background

        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.on_mouse_event)

        while not global_exit_flag:
            cv2.imshow(self.window_name, background)
            key_code = cv2.waitKey(20) & 0xFF

            if key_code == 27:
                break

            if key_code > 0:
                self.event_queue.put(Event(key_code=key_code))

        cv2.destroyAllWindows()

    def on_mouse_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.event_queue.put(Event(mouse_click=EVENT_MOUSE_LEFT_DOWN))
        elif event == cv2.EVENT_LBUTTONUP:
            self.event_queue.put(Event(mouse_click=EVENT_MOUSE_LEFT_UP))
        elif event == cv2.EVENT_MBUTTONDOWN:
            self.event_queue.put(Event(mouse_click=EVENT_MOUSE_MIDDLE_DOWN))

        self.event_queue.put(Event(mouse_pos=(x, y)))


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


#
# Video proxy that sets up an artificial video device and executes a list of render passes to augment it.
#
class VideoProxy(virtualvideo.VideoSource):
    def __init__(self, config, fps):
        logging.info("Video Proxy start")

        self.event_queue = queue.Queue()
        self.config = config

        self.fps_value = fps
        self.width = OUT_WIDTH
        self.height = OUT_HEIGHT

        self.output_rect = (self.width, self.height)

        self.videoInputOriginal = cv2.VideoCapture(IN_VIDEO_DEVICE_ID)

        self.output_render_passes = [
            StaticTextRenderPass("Video Proxy Demo v0.1"),
            RandomFlashRenderPass(),
            TypingTextRenderPass(),
            MorseCodeRenderPass(),
            PongRenderPass(),
            ShellWatcherRenderPass(["vmstat"], 10, 8),
            ShellWatcherRenderPass(["cat", "experiment/notepad.txt"], 10, 300, 30),
            MouseDrawRenderPass(),
            TimerRenderPass(),
            TemplateRecognitionDrawRenderPass(),
            RedDotDrawRenderPass(LineDrawer()),
            CarDrawRenderPass(),
        ]
        for i, render_pass in enumerate(self.output_render_passes):
            logging.info("Pass #" + str(i) + ": " + render_pass.name())

        # To keep window thread alive.
        self.__control_window = ControlWindow(self.event_queue)

    def img_size(self):
        return self.output_rect

    def fps(self):
        return self.fps_value

    def generator(self):
        global global_exit_flag
        global background

        output_render_pass_mask = 1
        is_pip_mode = False

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
                img[
                    0 : (self.height >> 2), 0 : (self.width >> 2)
                ] = default_video_resized
            else:
                img = cv2.resize(default_video, (self.width, self.height))

            # Move out accumulated UI events from the thread safe queue.
            events = []
            while self.event_queue.qsize() > 0:
                event = self.event_queue.get()
                events.append(event)

                # React on main app events (if there is any).
                key_code = event.key_code
                if key_code is not None and key_code > 0:
                    if key_code == 45:  # Key: -
                        output_render_pass_mask = OUTPUT_RENDER_PASS_MASK_ALL
                    elif key_code == 96:  # Key: `
                        output_render_pass_mask = OUTPUT_RENDER_PASS_MASK_NONE
                    elif key_code >= 48 and key_code <= 57:  # Key: 0..9
                        output_render_pass_mask ^= 1 << (key_code - 48)
                    elif key_code == 112:  # Key: p
                        is_pip_mode = not is_pip_mode

            # Execute render passes.
            used_passes = []
            for i, output_render_pass in enumerate(self.output_render_passes):
                pass_mask = 1 << i
                if output_render_pass_mask & pass_mask > 0:
                    img = output_render_pass.render(img, events)
                    used_passes.append(output_render_pass.name())

            # Printing active passes on the screen.
            img = cv2.flip(img, 1)
            for i, pass_name in enumerate(used_passes):
                cv2.putText(
                    img,
                    pass_name,
                    (self.width - 250, self.height - 20 - (i * 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    COLOR_WHITE,
                    2,
                )
            img = cv2.flip(img, 1)

            # Present frame to the fake device.
            yield img


# CTRL-C handler.
signal.signal(signal.SIGINT, sig_interrupt_handler)

config = EnvConfig()
fps = config.value_args.get(ARG_FPS) or OUT_FPS

# Setup app.
video_device = virtualvideo.FakeVideoDevice()
video_device.init_input(VideoProxy(config, fps))
video_device.init_output(OUT_VIDEO_DEVICE_ID, OUT_WIDTH, OUT_HEIGHT, fps)
video_device.run()
