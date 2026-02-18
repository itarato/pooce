import time

from conf import *
from shared import *


#
# Render pass that presents a countdown timer (coming from STDIN).
#
class TimerRenderPass(OutputRenderPass):
    def __init__(self):
        self.expire = None

    def name(self):
        return "Timer"

    def render(self, img, events, config: Config):
        line = non_block_stdin_get_line()
        if line is not None:
            seconds = int(line)
            self.expire = time.time() + seconds

        if self.expire is not None:
            diff = self.expire - time.time()
            if diff >= 0:
                text = str(int(diff * 100) / 100)  # Round to 2 digits.
            else:
                text = "Timer completed"

            cv2.putText(
                img,
                text,
                (OUT_WIDTH - 300, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                COLOR_ORANGE,
                2,
            )

        return img
