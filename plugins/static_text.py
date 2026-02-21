import cv2
import tkinter as tk
from conf import *
from shared import *


#
# Render pass that paints a fixed text.
#
class StaticTextRenderPass(OutputRenderPass):
    def __init__(self, text):
        self.var_text = None
        self.var_posx = None
        self.var_posy = None
        self.var_fontsize = None

    def name(self):
        return "Static text"

    def render(self, img, events, config: Config):
        cv2.putText(
            img,
            self.var_text.get(),
            (
                int(OUT_WIDTH * self.var_posx.get() / 100.0),
                int(OUT_HEIGHT * self.var_posy.get() / 100.0),
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            self.var_fontsize.get() / 10.0,
            COLOR_WHITE,
            int(self.var_fontsize.get() / 4.0),
            cv2.LINE_AA,
        )

        return img

    def gui_frame(self, parent):
        frame = tk.Frame(parent)

        self.var_text = tk.StringVar(value="Hello")
        self.var_posx = tk.IntVar(value=50)
        self.var_posy = tk.IntVar(value=50)
        self.var_fontsize = tk.IntVar(value=10)

        tk.Label(frame, text="Text:", width=14, anchor="e").grid(row=0, column=0)
        tk.Entry(frame, width=40, textvariable=self.var_text).grid(row=0, column=1)
        tk.Label(frame, text="X coordinate:", width=14, anchor="e").grid(
            row=1, column=0
        )
        tk.Scale(frame, variable=self.var_posx, orient="horizontal").grid(
            row=1, column=1, sticky="ew"
        )
        tk.Label(frame, text="Y coordinate:", width=14, anchor="e").grid(
            row=2, column=0
        )
        tk.Scale(frame, variable=self.var_posy, orient="horizontal").grid(
            row=2, column=1, sticky="ew"
        )
        tk.Label(frame, text="Font size:", width=14, anchor="e").grid(row=3, column=0)
        tk.Scale(frame, variable=self.var_fontsize, orient="horizontal").grid(
            row=3, column=1, sticky="ew"
        )

        return frame
