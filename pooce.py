import virtualvideo
import cv2
import random

OUT_WIDTH = 800
OUT_HEIGHT = 600


class OutputRenderPass:
    def render(self, img):
        NotImplementedError("Must be implemented")


class RandomFlashRenderPass(OutputRenderPass):
    def __init__(self):
        self.size = 10

    def render(self, img):
        rx = random.randrange(0, OUT_WIDTH - self.size)
        ry = random.randrange(0, OUT_HEIGHT - self.size)

        img[rx : (rx + self.size), ry : (ry + self.size)] = (0, 0, 255)

        return img


class VideoProxy(virtualvideo.VideoSource):
    def __init__(self):
        self.output_rect = (OUT_HEIGHT, OUT_WIDTH)

        self.videoInputOriginal = cv2.VideoCapture(0)

        self.output_render_passes = [RandomFlashRenderPass()]

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
video_device.init_output(2, 1280, 720, fps=30)
video_device.run()
