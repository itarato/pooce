import virtualvideo
import cv2
import random
import select
import sys
import numpy

OUT_WIDTH = 1280
OUT_HEIGHT = 720

IN_VIDEO_DEVICE_ID = 0
OUT_VIDEO_DEVICE_ID = 2

COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)


class OutputRenderPass:
    def render(self, img):
        NotImplementedError("Must be implemented")


class PongRenderPass(OutputRenderPass):
    def __init__(self):
        self.x = 10
        self.y = 10
        self.size = 16
        self.vx = 20
        self.vy = 20

    def render(self, img):
        x_candidate = self.x + self.vx
        y_candidate = self.y + self.vy

        if x_candidate < 0 or x_candidate > OUT_WIDTH:
            self.vx *= -1

        if y_candidate < 0 or y_candidate > OUT_HEIGHT:
            self.vy *= -1

        self.x += self.vx
        self.y += self.vy

        return cv2.circle(img, (self.x, self.y), self.size, COLOR_GREEN, -1)


class RandomFlashRenderPass(OutputRenderPass):
    def __init__(self):
        self.drops = [OUT_HEIGHT] * OUT_WIDTH
        self.speed = 50

    def render(self, img):
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

    def render(self, img):
        # TODO: Hflip.
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


class TypingTextRenderPass(OutputRenderPass):
    def __init__(self):
        self.texts = []

    def render(self, img):
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


class CarDrawRenderPass(OutputRenderPass):
    def __init__(self):
        self.net = cv2.dnn.readNetFromCaffe(
            "model/MobileNetSSD_deploy.prototxt",
            "model/MobileNetSSD_deploy.caffemodel",
        )
        self.map = [0] * (OUT_HEIGHT * OUT_WIDTH)

    def render(self, img):
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


class VideoProxy(virtualvideo.VideoSource):
    def __init__(self):
        self.output_rect = (OUT_WIDTH, OUT_HEIGHT)

        self.videoInputOriginal = cv2.VideoCapture(IN_VIDEO_DEVICE_ID)

        self.output_render_passes = [
            RandomFlashRenderPass(),
            StaticTextRenderPass("Pooce Demo v0"),
            TypingTextRenderPass(),
            PongRenderPass(),
            # CarDrawRenderPass(),
        ]

    def img_size(self):
        return self.output_rect

    def fps(self):
        return 10

    def generator(self):
        while True:
            _rval, frame = self.videoInputOriginal.read()
            frame_resized = cv2.resize(frame, self.output_rect)

            for output_render_pass in self.output_render_passes:
                frame_resized = output_render_pass.render(frame_resized)

            yield frame_resized


video_device = virtualvideo.FakeVideoDevice()
video_device.init_input(VideoProxy())
video_device.init_output(OUT_VIDEO_DEVICE_ID, OUT_WIDTH, OUT_HEIGHT, fps=30)
video_device.run()
