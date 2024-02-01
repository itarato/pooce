import numpy

ARG_FPS = "--fps"

OUT_WIDTH = 1280
OUT_HEIGHT = 720

# Target frame per seconds (not guaranteed).
OUT_FPS = 60

# Linux device numbers (/dev/video?).
IN_VIDEO_DEVICE_ID = 0
OUT_VIDEO_DEVICE_ID = 2

COLOR_BLACK = (0, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_PURPLE = (255, 0, 255)
COLOR_RED = (0, 0, 255)
COLOR_LAGUNA_BLUE = (255, 255, 0)
COLOR_MAGENTA = (255, 0, 255)
COLOR_ORANGE = (0, 150, 255)

# For main event handling.
EVENT_MOUSE_LEFT_DOWN = 1
EVENT_MOUSE_LEFT_UP = 2
EVENT_MOUSE_MIDDLE_DOWN = 3

# Mask to control which output renderer is enabled.
OUTPUT_RENDER_PASS_MASK_ALL = ~0
OUTPUT_RENDER_PASS_MASK_NONE = 1 << 10  # Have the demo logo shown.

# Dot value (x and y) that acts a no-draw/-follow marker.
DISCONTINUATION_DOT = -1

# For SIGINT to signal everyone.
global_exit_flag = False

# Default background.
background = numpy.zeros((OUT_HEIGHT, OUT_WIDTH, 3), numpy.uint8)
