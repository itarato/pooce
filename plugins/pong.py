import cv2
from shared import *


#
# Render pass that plays pong. Keys `a` and `d` are left/right.
#
class PongRenderPass(OutputRenderPass):
    def __init__(self):
        self.x = OUT_WIDTH >> 1
        self.y = OUT_HEIGHT >> 1
        self.size = 16
        self.speed = 20
        self.vx = self.speed
        self.vy = self.speed

        self.bat_x = OUT_WIDTH >> 1
        self.bat_size = 160
        self.score = 0

    def name(self):
        return "Pong (game)"

    def render(self, img, events: list[Event], config: Config):
        x_candidate = self.x + self.vx
        y_candidate = self.y + self.vy

        if (
            x_candidate < config.active_area_left_border()
            or x_candidate > config.active_area_right_border()
        ):
            self.vx *= -1

        if y_candidate < 0 or y_candidate > config.active_area_height():
            self.vy *= -1

        if (
            x_candidate >= (self.bat_x - (self.bat_size >> 1))
            and x_candidate <= (self.bat_x + (self.bat_size >> 1))
            and y_candidate >= (config.active_area_height() - 35)
        ):
            self.score += 1
            self.vy = -self.speed

        self.x += self.vx
        self.y += self.vy

        for event in events:
            if event.is_mouse_event():
                self.bat_x = config.relx(event.mouse_x_rel())

        cv2.rectangle(
            img,
            (self.bat_x - (self.bat_size >> 1), config.active_area_height() - 30),
            (self.bat_x + (self.bat_size >> 1), config.active_area_height()),
            COLOR_GREEN,
            -1,
        )

        cv2.putText(
            img,
            "Score: " + str(self.score),
            (
                self.bat_x - (self.bat_size >> 1),
                config.active_area_height() - 6,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            COLOR_BLACK,
            2,
        )

        return cv2.circle(img, (self.x, self.y), self.size, COLOR_GREEN, -1)
