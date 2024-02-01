# Video Proxy

Video proxy learning project: a video output stream (~webcam) that is programmable in Python.

## Setup

- `sudo apt install v4l2loopback-utils`
- `sudo modprobe v4l2loopback video_nr=2 exclusive_caps=1`
- `python -m venv ./.venv`
- `. .venv/bin/activate`
- `pip install -r requirements.txt`

## Run

- `python main.py`

## Controls

- 0-9: output render pass toggle
- `: turn off all render pass
- -: turn on all render pass
- p: toggle PIP mode
- ESC: kill UI event listener
- CTRL-C: exit
- a/d: pong left/right

## Current plugins

- static text
- real time typed text
- animation (rain)
- game (pong)
- car recognition drawing
- red dot recognition drawing
- template recognition drawing
- shell command watchdog
- mouse drawing

## Wishlist

- faster image recognition
- static text pass:
  - position / color
- configurable size + frame rate
- typing pass to be keypress granular (no enter)
- (!) apple system compatibility
- (!) horizontal flip fix
- morse plugin

## Troubleshooting

### Video is blocked

Start a video call session with the default video first and then only with the fake device and make sure to allow both separately.

Also make sure nothing uses the video stream before the first use after boot (eg browser restored state).

### Video device error

```
Couldn't write image to ffmpeg, error output of ffmpeg
...
[video4linux2,v4l2 @ 0x557783d6d8c0] ioctl(VIDIOC_G_FMT): Invalid argument
```

Solution:

```bash
sudo rmmod v4l2loopback
sudo modprobe v4l2loopback video_nr=2 exclusive_caps=1
```
