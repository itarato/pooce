import cv2

from conf import *
from shared import *


#
# Render pass that turns input to morse code.
#
class MorseCodeRenderPass(OutputRenderPass):
    def __init__(self):
        self.table = [
            [1, 3],  # a
            [3, 1, 1, 1],  # b
            [3, 1, 3, 1],  # c
            [3, 1, 1],  # d
            [1],  # e
            [1, 1, 3, 1],  # f
            [3, 3, 1],  # g
            [1, 1, 1, 1],  # h
            [1, 1],  # i
            [1, 3, 3, 3],  # j
            [3, 1, 3],  # k
            [1, 3, 1, 1],  # l
            [3, 3],  # m
            [3, 1],  # n
            [3, 3, 3],  # o
            [1, 3, 3, 1],  # p
            [3, 3, 1, 3],  # q
            [1, 3, 1],  # r
            [1, 1, 1],  # s
            [3],  # t
            [1, 1, 3],  # u
            [1, 1, 1, 3],  # v
            [1, 3, 3],  # w
            [3, 1, 1, 3],  # x
            [3, 1, 3, 3],  # y
            [3, 3, 1, 1],  # z
        ]
        self.queue = []
        self.counter = -1

        # How long a single unit will flash.
        self.tick_length = 6
        # Gap between letters.
        self.tick_gap = 3
        self.tick_letter_gap = 8

    def name(self):
        return "Morse code"

    def render(self, img, events):
        line = non_block_stdin_get_line()
        if line is not None:
            for c in line:
                c = c.lower()
                if c >= "a" and c <= "z":
                    self.queue += self.table[ord(c) - ord("a")]
                    self.queue.append(-1)  # Letter gap.

        if self.counter < 0:
            if len(self.queue) > 0:
                if self.queue[0] == -1:
                    self.counter = self.tick_letter_gap
                else:
                    self.counter = self.queue[0] * self.tick_length + self.tick_gap
        else:
            self.counter -= 1
            if self.counter < 0:
                self.queue = self.queue[1:]

        if self.counter >= self.tick_gap and self.queue[0] != -1:
            cv2.circle(img, (OUT_WIDTH >> 1, OUT_HEIGHT - 100), 42, COLOR_ORANGE, -1)

        return img
