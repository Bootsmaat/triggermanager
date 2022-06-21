# Triggermanager

# Description

Triggermanager is written as a front-end for [PiSync](https://github.com/IronJonas/PiSync). It provides the following features:

- monitoring data received from PLC by PiSync
- configuring PiSync settings
- playing audio / video qeues based on a trigger signal from the PLC.

**Make sure to use the `dev` branch as `master` outdated**

# Dependencies

- Python 3.8 (32 bit)
- Tkinter
- `python-vlc`
- VLC (32 bit)

# Installation

1. Make sure Python 3.8 is installed
2. Make sure Tkinter is installed along Python (should be by default)
3. Install VLC (make sure it's the 32bit)
4. Install `python-vlc` with `pip` (again, 32 bit)

# Usage

1. Make sure the raspberry running PiSync is on the same network as the host machine.
2. Start PiSync
3. Run `triggerman.py`
4. In the connect panel, enter the pi's IP address using the custom option
5. Once connected, open the fiz layout window
6. Set FIZ data to correct position. (position is defined in Maya export)
7. Add triggers as desired
8. There is an option to open a playback window for video playback. This can be opened fromt the video tab.
9. Once triggers are configured, press `send to pi`
10. Press `shoot` to start listening for trigger (will also cause FIZ values to update)
11. Press `shoot` again to exit shooting mode

# Troubleshooting

- It's best to monitor the PiSync application from the terminal as triggerman has a lot of bugs

# Future goals

- [ ] Arduino trigger
