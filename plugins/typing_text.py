import cv2

from conf import *
from shared import *


#
# Render pass that receives real time text input from STDIN.
# Use `/clear` to reset.
#
class TypingTextRenderPass(OutputRenderPass):
    def __init__(self):
        self.texts = []

    def name(self):
        return "STDIN typing"

    def render(self, img, events):
        line = non_block_stdin_get_line()
        if line is not None:
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
