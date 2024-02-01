import cv2

from conf import *
from shared import *


#
# Output pass that draws with the mouse. Middle button click is reset.
#
class MouseDrawRenderPass(OutputRenderPass):
    def __init__(self):
        self.is_mouse_down = False
        self.drawer = LineDrawer(COLOR_MAGENTA)
        self.last_pos = (0, 0)

    def name(self):
        return "Mouse drawing"

    def render(self, img, events):
        for event in events:
            if event.mouse_click == EVENT_MOUSE_LEFT_DOWN:
                self.is_mouse_down = True
            elif event.mouse_click == EVENT_MOUSE_LEFT_UP:
                self.is_mouse_down = False
                self.drawer.record(DISCONTINUATION_DOT, DISCONTINUATION_DOT)
            elif event.mouse_click == EVENT_MOUSE_MIDDLE_DOWN:
                self.drawer.reset()
            elif event.mouse_pos is not None:
                if self.is_mouse_down:
                    self.drawer.record(
                        OUT_WIDTH - event.mouse_pos[0], event.mouse_pos[1]
                    )

                self.last_pos = (OUT_WIDTH - event.mouse_pos[0], event.mouse_pos[1])

        self.drawer.draw(img)
        cv2.circle(img, self.last_pos, 8, COLOR_WHITE, 4)

        return img
