import cv2

from conf import *
from shared import *


#
# Output pass that draws with the mouse. Middle button click is reset.
#
class MouseDrawRenderPass(OutputRenderPass):
    def __init__(self):
        self.is_mouse_down = False
        self.drawer = LineDrawer(COLOR_ORANGE)
        self.last_pos = (0, 0)

    def name(self):
        return "Mouse drawing"

    def render(self, img, events, config: Config):
        # for event in events:
        #     if event.mouse_click == EVENT_MOUSE_LEFT_DOWN:
        #         self.is_mouse_down = True
        #     elif event.mouse_click == EVENT_MOUSE_LEFT_UP:
        #         self.is_mouse_down = False
        #         self.drawer.record(DISCONTINUATION_DOT, DISCONTINUATION_DOT)
        #     elif event.mouse_click == EVENT_MOUSE_MIDDLE_DOWN:
        #         self.drawer.reset()
        #     elif event.mouse_pos is not None:
        #         if self.is_mouse_down:
        #             self.drawer.record(event.mouse_pos[0], event.mouse_pos[1])

        #         self.last_pos = (event.mouse_pos[0], event.mouse_pos[1])

        self.drawer.draw(img)
        cv2.circle(img, self.last_pos, 8, COLOR_WHITE, 4)

        return img

    def gui_frame(self, parent):
        frame = tk.Frame(parent)

        canvas = tk.Canvas(frame, width=400, height=300, bg="gray")
        canvas.pack()

        def on_mouse_move(event):
            self.last_pos = (event.x, event.y)
            if self.is_mouse_down:
                self.drawer.record(event.x, event.y)

        def on_mouse_click(event):
            self.is_mouse_down = True

        def on_mouse_release(event):
            self.is_mouse_down = False
            self.drawer.record(DISCONTINUATION_DOT, DISCONTINUATION_DOT)

        canvas.bind("<Motion>", on_mouse_move)
        canvas.bind("<Button-1>", on_mouse_click)
        canvas.bind("<ButtonRelease-1>", on_mouse_release)

        return frame
