import cv2
import sys
import select
import tkinter as tk
from conf import *

EVENT_KIND_MOUSE_MOVE = 0
EVENT_KIND_MOUSE_CLICK = 1
EVENT_KIND_KEY_PRESS = 2
EVENT_KIND_TOGGLE_RENDER_PASS = 3


class ToggleEventData:
    def __init__(self, render_pass_index: int, is_on: bool):
        self.render_pass_index = render_pass_index
        self.is_on = is_on


#
# Event record for app level UI events.
#
class Event:
    def __init__(self, data):
        self.data = data

    def kind(self) -> int:
        if isinstance(self.data, ToggleEventData):
            return EVENT_KIND_TOGGLE_RENDER_PASS
        else:
            raise ValueError(f"Unknown event data type: {type(self.data)}")


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

    def gui_frame(self, parent):
        frame = tk.Frame(parent)

        tk.Label(text="HELLO").pack(fill="x", pady=6)

        return frame


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
