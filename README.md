# controller-bigpicture

Open Steam **Big Picture** automatically the moment you turn an Xbox controller on.

There is no built-in Steam setting for this. Valve's "Guide button focuses Steam"
trick needs Steam already running and a manual double-tap of the Xbox button. This
is a tiny background watcher that does it for real: it polls **XInput**, so it sees
the pad whether it connects over Bluetooth, the Xbox wireless dongle, or USB, and
fires Steam's Big Picture the instant a new controller appears.

> **Windows only.** It must run on native Windows Python &mdash; XInput is a host API
> and is invisible from inside WSL.

## Requirements

- Windows 10 or 11
- [Python for Windows](https://www.python.org/downloads/windows/) 3.8+, installed
  with **"Add python.exe to PATH"** checked
- Steam installed (Steam registers the `steam://` protocol handler)

No third-party packages &mdash; the watcher uses only the Python standard library.

## Quick start (test it)

```powershell
python controller_bigpicture.py
```

Leave that running and turn your controller on. Big Picture should open. Run it with
`python` (not `pythonw`) for this first test so you can see any error in the console.
Press `Ctrl+C` to stop.

## Run it silently at login

Install a Startup entry that launches the watcher with `pythonw.exe` (no console
window):

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

That drops a shortcut in your Startup folder, so it starts automatically every time
you sign in. The installer also prints a command to start it immediately without
rebooting.

To remove it:

```powershell
powershell -ExecutionPolicy Bypass -File .\uninstall.ps1
```

## Options

| Flag           | Effect |
| -------------- | ------ |
| _(none)_       | Watch for a **new** connection. A pad that is already on when the watcher starts is ignored, so rebooting with the controller on won't relaunch Big Picture. |
| `--launch-now` | Also fire if a controller is already connected at start. Use this if you usually boot with the pad already on and want Big Picture then too. |
| `--log`        | Write a timestamped log to `%LOCALAPPDATA%\controller-bigpicture\watcher.log`. Handy for confirming the silent `pythonw` instance is alive. |

## How it works

XInput exposes up to four controller slots. Once a second the watcher asks XInput
whether any slot is connected. On a transition from "none" to "connected" it calls
`os.startfile("steam://open/bigpicture")`, which hands off to Steam's protocol
handler (starting Steam first if it isn't running).

## Troubleshooting

- **Nothing happens when I run it.** Make sure you're using native Windows Python,
  not WSL. From PowerShell, `python -c "import os; print(os.name)"` must print `nt`.
- **`No XInput DLL found`.** Very old Windows only. `xinput1_3` ships with the
  DirectX End-User Runtime; install that and retry.
- **Big Picture doesn't open but there's no error.** Confirm the URL works at all:
  paste `steam://open/bigpicture` into Win+R and press Enter. If that does nothing,
  the issue is Steam's protocol handler, not this script.
- **It opens Big Picture on every reboot.** You're probably passing `--launch-now`,
  or your controller reports connected at login. Drop the flag &mdash; the default
  already ignores an already-on pad.

## Not on Windows?

- **Steam Deck / SteamOS** already boots into Gamepad UI; you don't need this.
- **macOS / Linux desktop** use a different controller API (IOKit / evdev), so the
  detection would need rewriting. Open an issue and say which.

## License

MIT &mdash; see [LICENSE](LICENSE).
