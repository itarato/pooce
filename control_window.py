import tkinter as tk
import queue

from shared import *


#
# App level control window for event collection (mouse and keyboard).
#
class ControlWindow:
    def __init__(
        self, event_queue: queue.Queue, output_render_passes: list[OutputRenderPass]
    ):
        self.event_queue = event_queue
        self.output_render_passes = output_render_passes
        self.render_pass_toggles = []

    def run(self):
        root = tk.Tk()

        canvas = tk.Canvas(root)

        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)

        main_layout = tk.Frame(canvas)
        main_layout.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=main_layout, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for render_pass in self.output_render_passes:
            toggle_var = tk.IntVar()
            self.render_pass_toggles.append(toggle_var)
            tk.Checkbutton(
                main_layout, text=render_pass.name(), variable=toggle_var
            ).pack(pady=6, padx=6, anchor="w")

        root.mainloop()

    # def update_window(self):
    # key_code = cv2.waitKey(20) & 0xFF

    # if key_code == 27:
    #     return

    # if key_code > 0:
    #     self.event_queue.put(Event(key_code=key_code))

    # def on_mouse_event(self, event, x, y, flags, param):
    #     if event == cv2.EVENT_LBUTTONDOWN:
    #         self.event_queue.put(Event(mouse_click=EVENT_MOUSE_LEFT_DOWN))
    #     elif event == cv2.EVENT_LBUTTONUP:
    #         self.event_queue.put(Event(mouse_click=EVENT_MOUSE_LEFT_UP))
    #     elif event == cv2.EVENT_MBUTTONDOWN:
    #         self.event_queue.put(Event(mouse_click=EVENT_MOUSE_MIDDLE_DOWN))

    #     self.event_queue.put(Event(mouse_pos=(x, y)))
