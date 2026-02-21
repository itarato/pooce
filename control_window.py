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
        self.render_pass_frames = []

    def render_pass_toggle_changed(self, index: int):
        is_on = self.render_pass_toggles[index].get() == 1
        self.event_queue.put(Event(ToggleEventData(index, is_on)))

        if is_on:
            self.render_pass_frames[index].pack(
                side="top", fill="x", padx=6, pady=(0, 6), anchor="w"
            )
        else:
            self.render_pass_frames[index].pack_forget()

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

        for i, render_pass in enumerate(self.output_render_passes):
            toggle_var = tk.IntVar()
            self.render_pass_toggles.append(toggle_var)
            tk.Checkbutton(
                main_layout,
                text=render_pass.name(),
                variable=toggle_var,
                command=lambda index=i: self.render_pass_toggle_changed(index),
            ).pack(pady=6, padx=6, anchor="w")

            render_pass_frame_outer = tk.Frame(main_layout)
            render_pass_frame_outer.pack(
                side="top", fill="x", padx=6, pady=(0, 6), anchor="w"
            )

            render_pass_frame = render_pass.gui_frame(render_pass_frame_outer)

            self.render_pass_frames.append(render_pass_frame)

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
