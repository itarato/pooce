import cv2
import numpy

from conf import *
from shared import *


#
# Render pass that draws at locations where a red dot is presented.
# Mouse middle click is reset.
#
# @link https://github.com/ChristophRahn/red-circle-detection/blob/master/red-circle-detection.py
#
class RedDotDrawRenderPass(OutputRenderPass):
    def __init__(self, drawer: DotDrawer):
        self.drawer = drawer

    def name(self):
        return "Red dot recognition (drawing)"

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
