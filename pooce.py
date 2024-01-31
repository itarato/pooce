import virtualvideo
import cv2
import random
import select
import sys
import numpy

OUT_WIDTH = 1280
OUT_HEIGHT = 720


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

        return cv2.circle(img, (self.x, self.y), self.size, (100, 255, 100), -1)


class RandomFlashRenderPass(OutputRenderPass):
    def __init__(self):
        self.size = 10

    def render(self, img):
        rx = random.randrange(0, OUT_WIDTH - self.size)
        ry = random.randrange(0, OUT_HEIGHT - self.size)

        img[rx : (rx + self.size), ry : (ry + self.size)] = (0, 0, 255)

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
            (50, OUT_HEIGHT - 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
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
            line = sys.stdin.readline()
            self.texts.append(line.strip())

        img = cv2.flip(img, 1)

        for i, text in enumerate(self.texts):
            cv2.putText(
                img,
                text,
                (50, 25 + (i * 50)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
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

        self.videoInputOriginal = cv2.VideoCapture(0)

        self.output_render_passes = [
            RandomFlashRenderPass(),
            StaticTextRenderPass("Pooce Demo v0"),
            TypingTextRenderPass(),
            PongRenderPass(),
            CarDrawRenderPass(),
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
video_device.init_output(2, OUT_WIDTH, OUT_HEIGHT, fps=30)
video_device.run()
