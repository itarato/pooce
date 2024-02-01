import random
from shared import *


#
# This render pass demonstrates 2D graphics animation (rain).
#
class RandomFlashRenderPass(OutputRenderPass):
    def __init__(self):
        self.drops = [OUT_HEIGHT] * OUT_WIDTH
        self.speed = 50

    def name(self):
        return "Rain (animation)"

    def render(self, img, events):
        if random.random() < 0.4:
            self.drops[random.randrange(0, OUT_WIDTH)] = 0

        for x, y in enumerate(self.drops):
            if y < OUT_HEIGHT:
                self.drops[x] += self.speed
                img[y : (y + 20), x : (x + 10)] = COLOR_BLUE

        return img
