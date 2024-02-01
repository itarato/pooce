import cv2
import numpy

from conf import *
from shared import *


#
# Render pass that draws by tracking shapes. Currently it's looking for cars, though
# it's crazy bad and inefficient. It has troubles with moving and lights.
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

    def name(self):
        return "Car recognition (drawing)"

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
            # For reference.
            # CLASSES = [
            #     "background",
            #     "aeroplane",
            #     "bicycle",
            #     "bird",
            #     "boat",
            #     "bottle",
            #     "bus",
            #     "car",
            #     "cat",
            #     "chair",
            #     "cow",
            #     "diningtable",
            #     "dog",
            #     "horse",
            #     "motorbike",
            #     "person",
            #     "pottedplant",
            #     "sheep",
            #     "sofa",
            #     "train",
            #     "tvmonitor",
            # ]
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
