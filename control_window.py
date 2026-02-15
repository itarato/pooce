import cv2
import queue

from shared import *


#
# App level control window for event collection (mouse and keyboard).
#
class ControlWindow:
    def __init__(self, event_queue: queue.Queue):
        self.window_name = "pooce-mouse"
        self.event_queue = event_queue

    def start_window(self):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.on_mouse_event)

    def finish_window(self):
        cv2.destroyAllWindows()

    def update_window(self):
        global background

        cv2.imshow(self.window_name, background)
        key_code = cv2.waitKey(20) & 0xFF

        if key_code == 27:
            return

        if key_code > 0:
            self.event_queue.put(Event(key_code=key_code))

    def on_mouse_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.event_queue.put(Event(mouse_click=EVENT_MOUSE_LEFT_DOWN))
        elif event == cv2.EVENT_LBUTTONUP:
            self.event_queue.put(Event(mouse_click=EVENT_MOUSE_LEFT_UP))
        elif event == cv2.EVENT_MBUTTONDOWN:
            self.event_queue.put(Event(mouse_click=EVENT_MOUSE_MIDDLE_DOWN))

        self.event_queue.put(Event(mouse_pos=(x, y)))
