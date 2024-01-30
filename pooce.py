import virtualvideo
import cv2


class MyVideoSource(virtualvideo.VideoSource):
    def __init__(self):
        width = 800
        height = 600
        self.output_rect = (height, width)

        self.videoInputOriginal = cv2.VideoCapture(0)

    def img_size(self):
        return self.output_rect

    def fps(self):
        return 10

    def generator(self):
        while True:
            _rval, frame = self.videoInputOriginal.read()
            frame_resized = cv2.resize(frame, self.output_rect)
            yield frame_resized


vidsrc = MyVideoSource()

fvd = virtualvideo.FakeVideoDevice()
fvd.init_input(vidsrc)
fvd.init_output(2, 1280, 720, fps=30)
fvd.run()
