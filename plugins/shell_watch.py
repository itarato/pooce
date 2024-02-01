import subprocess
import cv2

from conf import *
from shared import *


#
# Render pass that can execute a shell command and paint STDOUT to the frame.
#
class ShellWatcherRenderPass(OutputRenderPass):
    def __init__(self, cmd_parts, frequency=10, x=OUT_WIDTH >> 1, y=OUT_HEIGHT >> 1):
        self.cmd_parts = cmd_parts

        # To limit drawing to every frequency-th frame.
        self.frequency = frequency
        self.counter = frequency
        self.output = []

        self.x = x
        self.y = y

    def name(self):
        return "Shell command (" + " ".join(self.cmd_parts) + ")"

    def render(self, img, events):
        if self.counter >= self.frequency:
            self.counter = 0

            output_bytes = subprocess.check_output(self.cmd_parts)
            output_utf8 = output_bytes.decode("utf-8")
            self.output = output_utf8.split("\n")
        else:
            self.counter += 1

        img = cv2.flip(img, 1)

        for i, line in enumerate(self.output):
            cv2.putText(
                img,
                line,
                (self.x, self.y + (i * 35)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                COLOR_BLACK,
                4,
                cv2.LINE_AA,
            )
            cv2.putText(
                img,
                line,
                (self.x, self.y + (i * 35)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                COLOR_WHITE,
                2,
                cv2.LINE_AA,
            )

        img = cv2.flip(img, 1)

        return img
