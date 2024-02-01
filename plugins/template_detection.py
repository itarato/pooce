import cv2

from conf import *
from shared import *


#
# Output pass that uses fixed template (pattern) recognition for drawing.
#
class TemplateRecognitionDrawRenderPass(OutputRenderPass):
    def __init__(self):
        self.template = cv2.imread("model/template.png", cv2.IMREAD_GRAYSCALE)
        self.w, self.h = self.template.shape[::-1]
        self.drawer = SimpleDotDrawer()

    def name(self):
        return "Template recognition (drawing)"

    def render(self, img, events):
        for event in events:
            if event.mouse_click == EVENT_MOUSE_MIDDLE_DOWN:
                self.drawer.reset()

        img_grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply template Matching
        res = cv2.matchTemplate(img_grayscale, self.template, cv2.TM_CCOEFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc

        self.drawer.record(top_left[0] + (self.w >> 1), top_left[1] + (self.h >> 1))

        self.drawer.draw(img)

        return img
