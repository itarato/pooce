import cv2
import sys
import select

from conf import *


#
# Event record for app level UI events.
#
class Event:
    def __init__(self, mouse_pos=None, mouse_click=None, key_code=None):
        self.mouse_pos = mouse_pos
        self.mouse_click = mouse_click
        self.key_code = key_code


#
# Drawing interface for dot level painting (each input is a single coordinate).
#
class DotDrawer:
    def record(self, x, y):
        NotImplementedError("Must be implemented")

    def draw(self, img):
        NotImplementedError("Must be implemented")

    def reset(self):
        NotImplementedError("Must be implemented")


#
# Dot drawer that only draws dots as they were registered.
#
class SimpleDotDrawer(DotDrawer):
    def __init__(self, color=COLOR_RED):
        self.reset()
        self.color = color

    def record(self, x, y):
        if x == DISCONTINUATION_DOT or y == DISCONTINUATION_DOT:
            return

        self.map[(OUT_WIDTH * y) + x] = 1

    def draw(self, img):
        for y in range(OUT_HEIGHT):
            for x in range(OUT_WIDTH):
                if self.map[(y * OUT_WIDTH) + x] > 0:
                    cv2.circle(img, (x, y), 4, self.color, -1)

    def reset(self):
        self.map = [0] * (OUT_HEIGHT * OUT_WIDTH)


#
# Dot drawer that draws lines using the received sequence of dots.
#
class LineDrawer(DotDrawer):
    def __init__(self, color=COLOR_RED):
        self.sequence = []
        self.color = color

    def record(self, x, y):
        self.sequence.append((x, y))

    def draw(self, img):
        if len(self.sequence) == 0:
            return

        for i in range(len(self.sequence) - 1):
            if (
                DISCONTINUATION_DOT in self.sequence[i]
                or DISCONTINUATION_DOT in self.sequence[i + 1]
            ):
                continue

            cv2.line(img, self.sequence[i], self.sequence[i + 1], self.color, 4)

    def reset(self):
        self.sequence.clear()


#
# A render pass is a unit of code that can interact with the output frame. The returned image will be drawn
# (eventually) to the output video stream. Events are coming from the apps main event collector window
# (mouse and key).
#
class OutputRenderPass:
    def name(self):
        NotImplementedError("Must be implemented")

    def render(self, img, events):
        NotImplementedError("Must be implemented")


def non_block_stdin_get_line():
    if select.select(
        [
            sys.stdin,
        ],
        [],
        [],
        0.0,
    )[0]:
        return sys.stdin.readline().strip()
    else:
        return None
