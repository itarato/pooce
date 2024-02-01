import cv2
from shared import *


#
# Render pass that plays pong. Keys `a` and `d` are left/right.
#
class PongRenderPass(OutputRenderPass):
    def __init__(self):
        self.x = 10
        self.y = 10
        self.size = 16
        self.speed = 20
        self.vx = self.speed
        self.vy = self.speed

        self.bat_x = OUT_WIDTH >> 1
        self.bat_size = 160
        self.score = 0

    def name(self):
        return "Pong (game)"

    def render(self, img, events):
        x_candidate = self.x + self.vx
        y_candidate = self.y + self.vy

        if x_candidate < 0 or x_candidate > OUT_WIDTH:
            self.vx *= -1

        if y_candidate < 0 or y_candidate > OUT_HEIGHT:
            self.vy *= -1

        if (
            x_candidate >= (self.bat_x - (self.bat_size >> 1))
            and x_candidate <= (self.bat_x + (self.bat_size >> 1))
            and y_candidate >= (OUT_HEIGHT - 35)
        ):
            self.score += 1
            self.vy = -self.speed

        self.x += self.vx
        self.y += self.vy

        for event in events:
            if event.mouse_pos is not None:
                self.bat_x = OUT_WIDTH - event.mouse_pos[0]

        cv2.rectangle(
            img,
            (self.bat_x - (self.bat_size >> 1), OUT_HEIGHT - 30),
            (self.bat_x + (self.bat_size >> 1), OUT_HEIGHT),
            COLOR_GREEN,
            -1,
        )

        img = cv2.flip(img, 1)
        cv2.putText(
            img,
            "Score: " + str(self.score),
            (OUT_WIDTH - self.bat_x - (self.bat_size >> 1), OUT_HEIGHT - 6),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            COLOR_BLACK,
            2,
        )
        img = cv2.flip(img, 1)

        return cv2.circle(img, (self.x, self.y), self.size, COLOR_GREEN, -1)
