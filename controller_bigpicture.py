#!/usr/bin/env python3
"""controller-bigpicture - open Steam Big Picture when an Xbox controller turns on.

The watcher polls XInput once a second. The instant a controller goes from
"none connected" to "connected" on any of the four XInput slots, it fires the
Steam protocol URL that opens Big Picture / Gamepad UI.

Windows only. Run it with native Windows Python - XInput is a host API and is
not reachable from inside WSL.

Usage:
    python controller_bigpicture.py              # watch; ignore a pad already on at start
    python controller_bigpicture.py --launch-now # also fire if a pad is already on
    python controller_bigpicture.py --log        # write a log to %LOCALAPPDATA%
"""

from __future__ import annotations

import ctypes
import os
import sys
import time
from datetime import datetime

# --- configuration ---------------------------------------------------------

# XInput supports up to four controller slots (0-3).
XINPUT_MAX_CONTROLLERS = 4

# XInputGetState success return code.
ERROR_SUCCESS = 0

# How often to check, in seconds. One second is responsive without busy-waiting.
POLL_INTERVAL_SECONDS = 1.0

# steam://open/bigpicture hands off to Steam's protocol handler and opens the
# Big Picture / Gamepad UI. Steam does not need to be in the foreground; if it
# is closed, the handler starts it first.
STEAM_BIGPICTURE_URL = "steam://open/bigpicture"


# --- xinput plumbing -------------------------------------------------------

class _XInputState(ctypes.Structure):
    # We never read the gamepad payload, but XInputGetState needs somewhere to
    # write it. dwPacketNumber + a 16-byte gamepad blob matches XINPUT_STATE.
    _fields_ = [
        ("dwPacketNumber", ctypes.c_uint32),
        ("Gamepad", ctypes.c_byte * 16),
    ]


def load_xinput() -> "ctypes.WinDLL":
    """Load the newest XInput runtime present on this machine.

    xinput1_4 ships with Windows 8 and later. Older systems may only have the
    DirectX-redistributable 1_3 or the 9.1.0 stub, so we fall back in order.
    """
    for name in ("xinput1_4", "xinput1_3", "xinput9_1_0"):
        try:
            return ctypes.windll.LoadLibrary(name)
        except OSError:
            continue
    raise RuntimeError(
        "No XInput DLL found. This script must run on native Windows "
        "(not WSL), where xinput1_4/1_3 is available."
    )


def any_controller_connected(xinput: "ctypes.WinDLL") -> bool:
    state = _XInputState()
    for slot in range(XINPUT_MAX_CONTROLLERS):
        if xinput.XInputGetState(slot, ctypes.byref(state)) == ERROR_SUCCESS:
            return True
    return False


def launch_big_picture() -> None:
    # os.startfile uses ShellExecute, which respects the steam:// protocol
    # handler. (webbrowser.open would try a browser for non-http URLs.)
    os.startfile(STEAM_BIGPICTURE_URL)


# --- logging (optional) ----------------------------------------------------

def make_logger(enabled: bool):
    if not enabled:
        return lambda msg: None

    log_dir = os.path.join(
        os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
        "controller-bigpicture",
    )
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "watcher.log")

    def log(msg: str) -> None:
        line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
        try:
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except OSError:
            pass
        # Also echo to stdout for when run via `python` (not pythonw).
        print(line, flush=True)

    return log


# --- main loop -------------------------------------------------------------

def main() -> int:
    launch_now = "--launch-now" in sys.argv
    log = make_logger("--log" in sys.argv)

    try:
        xinput = load_xinput()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    # Seed with the current state so a controller that was already on when the
    # watcher starts does NOT trigger a launch. --launch-now opts into firing on
    # that first detection instead (handy if you boot with the pad already on).
    was_connected = False if launch_now else any_controller_connected(xinput)
    log(f"watching (launch_now={launch_now}, seeded connected={was_connected})")

    while True:
        is_connected = any_controller_connected(xinput)
        if is_connected and not was_connected:
            log("controller connected -> opening Big Picture")
            try:
                launch_big_picture()
            except OSError as exc:
                log(f"failed to launch Big Picture: {exc}")
        was_connected = is_connected
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
