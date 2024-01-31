# POOCE V0

Video proxy learning project.

- https://github.com/Flashs/virtualvideo
- https://github.com/umlaeute/v4l2loopback
- make sure you're running both real cam and fake cam feeds (supported by a non-cam copy) to allow them in the browser
- `sudo apt install v4l2loopback-utils`
- `sudo modprobe v4l2loopback video_nr=2 exclusive_caps=1`
- `python -m venv ./.venv`
- `. .venv/bin/activate`
- `pip install -r requirements.txt`
