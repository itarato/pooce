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
import random
import select
import sys
import numpy
import subprocess
import threading
import queue
import time
import signal

OUT_WIDTH = 1280
OUT_HEIGHT = 720

# Target frame per seconds (not guaranteed).
OUT_FPS = 60

# Linux device numbers (/dev/video?).
IN_VIDEO_DEVICE_ID = 0
OUT_VIDEO_DEVICE_ID = 2

COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_PURPLE = (255, 0, 255)
COLOR_RED = (0, 0, 255)
COLOR_LAGUNA_BLUE = (255, 255, 0)

# For main event handling.
EVENT_MOUSE_LEFT_DOWN = 1
EVENT_MOUSE_LEFT_UP = 2
EVENT_MOUSE_MIDDLE_DOWN = 3

# Mask to control which output renderer is enabled.
OUTPUT_RENDER_PASS_MASK_ALL = -1

# For SIGINT to signal everyone.
global_exit_flag = False


def sig_interrupt_handler(sig, frame):
    global global_exit_flag
    global_exit_flag = True

    time.sleep(1)
    print("\nExiting Pooce\n")

    sys.exit(0)


#
# Event record for app level UI events.
#
class Event:
    def __init__(self, mouse_pos=None, mouse_click=None, key_code=None):
        self.mouse_pos = mouse_pos
        self.mouse_click = mouse_click
        self.key_code = key_code


#
# Drawing interface for dot level painting (each input is a single coordinate).
#
class DotDrawer:
    def record(self, x, y):
        NotImplementedError("Must be implemented")

    def draw(self, img):
        NotImplementedError("Must be implemented")

    def reset(self):
        NotImplementedError("Must be implemented")


class SimpleDotDrawer(DotDrawer):
    def __init__(self, color=COLOR_RED):
        self.reset()
        self.color = color

    def record(self, x, y):
        self.map[(OUT_WIDTH * y) + x] = 1

    def draw(self, img):
        for y in range(OUT_HEIGHT):
            for x in range(OUT_WIDTH):
                if self.map[(y * OUT_WIDTH) + x] > 0:
                    cv2.circle(img, (x, y), 4, self.color, -1)

    def reset(self):
        self.map = [0] * (OUT_HEIGHT * OUT_WIDTH)


class LineDrawer(DotDrawer):
    def __init__(self):
        self.sequence = []

    def record(self, x, y):
        self.sequence.append((x, y))

    def draw(self, img):
        if len(self.sequence) == 0:
            return

        for i in range(len(self.sequence) - 1):
            cv2.line(img, self.sequence[i], self.sequence[i + 1], COLOR_RED, 4)

    def reset(self):
        self.sequence.clear()


class OutputRenderPass:
    def render(self, img, events):
        NotImplementedError("Must be implemented")


class PongRenderPass(OutputRenderPass):
    def __init__(self):
        self.x = 10
        self.y = 10
        self.size = 16
        self.speed = 20
        self.vx = self.speed
        self.vy = self.speed

        self.bat_x = OUT_WIDTH >> 1
        self.bat_size = 160
        self.score = 0

    def render(self, img, events):
        x_candidate = self.x + self.vx
        y_candidate = self.y + self.vy

        if x_candidate < 0 or x_candidate > OUT_WIDTH:
            self.vx *= -1

        if y_candidate < 0 or y_candidate > OUT_HEIGHT:
            self.vy *= -1

        if (
            x_candidate >= (self.bat_x - (self.bat_size >> 1))
            and x_candidate <= (self.bat_x + (self.bat_size >> 1))
            and y_candidate >= (OUT_HEIGHT - 35)
        ):
            self.score += 1
            self.vy = -self.speed

        self.x += self.vx
        self.y += self.vy

        for event in events:
            if event.key_code == 97:
                self.bat_x += 20
            elif event.key_code == 100:
                self.bat_x -= 20

        cv2.rectangle(
            img,
            (self.bat_x - (self.bat_size >> 1), OUT_HEIGHT - 30),
            (self.bat_x + (self.bat_size >> 1), OUT_HEIGHT),
            COLOR_GREEN,
            -1,
        )

        img = cv2.flip(img, 1)
        cv2.putText(
            img,
            "Score: " + str(self.score),
            (OUT_WIDTH - self.bat_x - (self.bat_size >> 1), OUT_HEIGHT - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            COLOR_BLACK,
            2,
        )
        img = cv2.flip(img, 1)

        return cv2.circle(img, (self.x, self.y), self.size, COLOR_GREEN, -1)


class RandomFlashRenderPass(OutputRenderPass):
    def __init__(self):
        self.drops = [OUT_HEIGHT] * OUT_WIDTH
        self.speed = 50

    def render(self, img, events):
        if random.random() < 0.4:
            self.drops[random.randrange(0, OUT_WIDTH)] = 0

        for x, y in enumerate(self.drops):
            if y >= OUT_HEIGHT:
                continue
            self.drops[x] += self.speed
            img[y : (y + 20), x : (x + 10)] = COLOR_BLUE

        return img


class StaticTextRenderPass(OutputRenderPass):
    def __init__(self, text):
        self.text = text

    def render(self, img, events):
        img = cv2.flip(img, 1)

        cv2.putText(
            img,
            self.text,
            (8, OUT_HEIGHT - 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            COLOR_WHITE,
            2,
            cv2.LINE_AA,
        )

        return cv2.flip(img, 1)


class ShellWatcherRenderPass(OutputRenderPass):
    def __init__(self, cmd_parts, frequency=10, x=OUT_WIDTH >> 1, y=OUT_HEIGHT >> 1):
        self.cmd_parts = cmd_parts

        self.frequency = frequency
        self.counter = frequency
        self.output = []

        self.x = x
        self.y = y

    def render(self, img, events):
        if self.counter >= self.frequency:
            self.counter = 0

            output_bytes = subprocess.check_output(self.cmd_parts)
            output_utf8 = output_bytes.decode("utf-8")
            self.output = output_utf8.split("\n")
        else:
            self.counter += 1

        img = cv2.flip(img, 1)

        for i, line in enumerate(self.output):
            cv2.putText(
                img,
                line,
                (self.x, self.y + (i * 35)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                COLOR_BLACK,
                4,
                cv2.LINE_AA,
            )
            cv2.putText(
                img,
                line,
                (self.x, self.y + (i * 35)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                COLOR_WHITE,
                2,
                cv2.LINE_AA,
            )

        img = cv2.flip(img, 1)

        return img


class TypingTextRenderPass(OutputRenderPass):
    def __init__(self):
        self.texts = []

    def render(self, img, events):
        if select.select(
            [
                sys.stdin,
            ],
            [],
            [],
            0.0,
        )[0]:
            line = sys.stdin.readline().strip()

            if line == "/clear":
                self.texts.clear()
            else:
                self.texts.append(line)

        img = cv2.flip(img, 1)

        for i, text in enumerate(self.texts):
            cv2.putText(
                img,
                text,
                (8, 25 + (i * 30)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                COLOR_BLACK,
                4,
                cv2.LINE_AA,
            )
            cv2.putText(
                img,
                text,
                (8, 25 + (i * 30)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                COLOR_WHITE,
                2,
                cv2.LINE_AA,
            )

        return cv2.flip(img, 1)


#
# @link https://medium.com/featurepreneur/object-detection-using-single-shot-multibox-detection-ssd-and-opencvs-deep-neural-network-dnn-d983e9d52652
#
class CarDrawRenderPass(OutputRenderPass):
    def __init__(self):
        self.net = cv2.dnn.readNetFromCaffe(
            "model/MobileNetSSD_deploy.prototxt",
            "model/MobileNetSSD_deploy.caffemodel",
        )
        self.map = [0] * (OUT_HEIGHT * OUT_WIDTH)

    def render(self, img, events):
        blob = cv2.dnn.blobFromImage(img, 0.007843, (300, 300), 127.5)
        h, w = img.shape[:2]
        self.net.setInput(blob)
        detections = self.net.forward()

        for i in numpy.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence <= 0.5:
                continue

            idx = int(detections[0, 0, i, 1])
            if idx != 7:
                continue

            box = detections[0, 0, i, 3:7] * numpy.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            if (
                startX >= 0
                and startX < OUT_WIDTH
                and startY >= 0
                and startY < OUT_HEIGHT
            ):
                self.map[(startY * OUT_WIDTH) + startX] = 1

        for y in range(OUT_HEIGHT):
            for x in range(OUT_WIDTH):
                if self.map[(y * OUT_WIDTH) + x] == 0:
                    continue
                cv2.circle(img, (x, y), 4, (0, 0, 255), -1, cv2.LINE_AA)

        return img


#
# @link https://github.com/ChristophRahn/red-circle-detection/blob/master/red-circle-detection.py
#
class RedDotDrawRenderPass(OutputRenderPass):
    def __init__(self, drawer: DotDrawer):
        self.drawer = drawer

    def render(self, img, events):
        for event in events:
            if event.mouse_click == EVENT_MOUSE_MIDDLE_DOWN:
                self.drawer.reset()

        captured_frame = img

        # Convert original image to BGR, since Lab is only available from BGR
        captured_frame_bgr = cv2.cvtColor(captured_frame, cv2.COLOR_BGRA2BGR)
        # First blur to reduce noise prior to color space conversion
        captured_frame_bgr = cv2.medianBlur(captured_frame_bgr, 3)
        # Convert to Lab color space, we only need to check one channel (a-channel) for red here
        captured_frame_lab = cv2.cvtColor(captured_frame_bgr, cv2.COLOR_BGR2Lab)
        # Threshold the Lab image, keep only the red pixels
        # Possible yellow threshold: [20, 110, 170][255, 140, 215]
        # Possible blue threshold: [20, 115, 70][255, 145, 120]
        captured_frame_lab_red = cv2.inRange(
            captured_frame_lab,
            numpy.array([20, 150, 150]),
            numpy.array([190, 255, 255]),
        )
        # Second blur to reduce more noise, easier circle detection
        captured_frame_lab_red = cv2.GaussianBlur(captured_frame_lab_red, (5, 5), 2, 2)
        # Use the Hough transform to detect circles in the image
        circles = cv2.HoughCircles(
            captured_frame_lab_red,
            cv2.HOUGH_GRADIENT,
            1,
            captured_frame_lab_red.shape[0] / 8,
            param1=100,
            param2=18,
            minRadius=5,
            maxRadius=60,
        )

        if circles is not None:
            circles = numpy.round(circles[0, :]).astype("int")
            self.drawer.record(circles[0, 0], circles[0, 1])

        self.drawer.draw(img)

        return img


class MouseDrawRenderPass(OutputRenderPass):
    def __init__(self):
        self.is_mouse_down = False
        self.drawer = SimpleDotDrawer(COLOR_LAGUNA_BLUE)
        self.last_pos = (0, 0)

    def render(self, img, events):
        for event in events:
            if event.mouse_click == EVENT_MOUSE_LEFT_DOWN:
                self.is_mouse_down = True
            elif event.mouse_click == EVENT_MOUSE_LEFT_UP:
                self.is_mouse_down = False
            elif event.mouse_click == EVENT_MOUSE_MIDDLE_DOWN:
                self.drawer.reset()
            elif event.mouse_pos is not None:
                if self.is_mouse_down:
                    self.drawer.record(
                        OUT_WIDTH - event.mouse_pos[0], event.mouse_pos[1]
                    )

                self.last_pos = (OUT_WIDTH - event.mouse_pos[0], event.mouse_pos[1])

        self.drawer.draw(img)
        cv2.circle(img, self.last_pos, 8, COLOR_WHITE, 4)

        return img


class ControlWindow:
    def __init__(self, event_queue: queue.Queue):
        self.window_name = "pooce-mouse"
        self.event_queue = event_queue
        threading.Thread(target=self.window_thread).start()

    def window_thread(self):
        global global_exit_flag

        cv2.namedWindow(self.window_name)
        background = numpy.zeros((OUT_HEIGHT, OUT_WIDTH, 3), numpy.uint8)
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


class VideoProxy(virtualvideo.VideoSource):
    def __init__(self):
        self.event_queue = queue.Queue()

        self.output_rect = (OUT_WIDTH, OUT_HEIGHT)

        self.videoInputOriginal = cv2.VideoCapture(IN_VIDEO_DEVICE_ID)

        self.output_render_passes = [
            StaticTextRenderPass("Pooce Demo v0"),  # 0
            RedDotDrawRenderPass(LineDrawer()),  # 1
            CarDrawRenderPass(),  # 2
            RandomFlashRenderPass(),  # 3
            TypingTextRenderPass(),  # 4
            PongRenderPass(),  # 5
            ShellWatcherRenderPass(["vmstat"], 10, 8),  # 6
            MouseDrawRenderPass(),  # 7
            ShellWatcherRenderPass(["cat", "experiment/notepad.txt"], 10, 300, 30),  # 8
        ]

        self.__control_window = ControlWindow(self.event_queue)

    def img_size(self):
        return self.output_rect

    def fps(self):
        return OUT_FPS

    def generator(self):
        global global_exit_flag
        output_render_pass_mask = 0  # First pass visible by default.

        while not global_exit_flag:
            _rval, frame = self.videoInputOriginal.read()
            frame_resized = cv2.resize(frame, self.output_rect)

            events = []
            while self.event_queue.qsize() > 0:
                event = self.event_queue.get()
                events.append(event)

                key_code = event.key_code
                if key_code is not None and key_code > 0:
                    if key_code == 45:  # Key: -
                        output_render_pass_mask = OUTPUT_RENDER_PASS_MASK_ALL
                    elif key_code >= 48 and key_code <= 57:  # Key: 0..9
                        output_render_pass_mask = key_code - 48

            for i, output_render_pass in enumerate(self.output_render_passes):
                if (
                    output_render_pass_mask == OUTPUT_RENDER_PASS_MASK_ALL
                    or i == output_render_pass_mask % len(self.output_render_passes)
                ):
                    frame_resized = output_render_pass.render(frame_resized, events)

            yield frame_resized


signal.signal(signal.SIGINT, sig_interrupt_handler)

video_device = virtualvideo.FakeVideoDevice()
video_device.init_input(VideoProxy())
video_device.init_output(OUT_VIDEO_DEVICE_ID, OUT_WIDTH, OUT_HEIGHT, fps=OUT_FPS)
video_device.run()
