import cv2
import tkinter as tk
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

    def render(self, img, events, config: Config):
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

        return img

    # def gui_frame(self, parent):
