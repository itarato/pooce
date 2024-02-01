import cv2
from conf import *
from shared import *


#
# Render pass that paints a fixed text.
#
class StaticTextRenderPass(OutputRenderPass):
    def __init__(self, text):
        self.text = text

    def name(self):
        return "Static text"

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
