# controller-bigpicture on iOS

**Short version:** iOS won't do exactly what the Windows version does, and that's a
platform limitation rather than a missing feature. Two realistic setups get you most of
the way &mdash; pick whichever matches what you actually want.

## Why it's different on iOS

- **No background watcher.** iOS doesn't let an app sit in the background polling for
  controller connections and launching other apps. The Windows version is a daemon;
  iOS has no equivalent.
- **No "Big Picture" on iPhone.** Big Picture / Gamepad UI is a desktop Steam mode. On
  iOS there's the Steam mobile app and **Steam Link** (which streams games from your
  PC), but no Big Picture to open.
- **A controller pairs to one device at a time.** If the pad is connected to your PC it
  is *not* connected to your iPhone, and vice-versa. That rules out "controller turns on
  &rarr; iPhone notices &rarr; PC opens Big Picture" as a single automatic flow.

So instead:

---

## Option 1 &mdash; Controller connects to iPhone &rarr; open a game app (no code)

The on-device equivalent: pair the Xbox controller to the iPhone, and when it connects,
iOS opens Steam Link (or any app). Pure Shortcuts, nothing to install.

**Requirements:** an Xbox *Bluetooth* controller (Xbox One S / Series and newer), iOS 16
or later recommended, and the app you want to open (e.g. Steam Link).

1. **Pair the controller:** Settings &rarr; Bluetooth, hold the controller's pair button
   until it appears, tap to connect.
2. Open the **Shortcuts** app &rarr; **Automation** tab &rarr; **+** &rarr; **Create
   Personal Automation**.
3. Choose **Bluetooth**. Under *Device*, pick your **Xbox Wireless Controller**. This
   fires whenever that controller connects.
4. **Next** &rarr; **New Blank Automation** (or **Add Action**) &rarr; search **Open
   App** &rarr; pick **Steam Link** (or Steam, or a game).
5. **Next**, then turn **Run Immediately** on and **Ask Before Running** off so it's
   fully automatic.

Now turn the controller on near your iPhone: it connects and opens Steam Link
automatically. Steam Link then streams Big Picture from your PC if you want the full
couch experience.

---

## Option 2 &mdash; iPhone as a remote that opens Big Picture on the PC

Keep the controller paired to the **PC**, and use the iPhone purely as a button that
tells the PC to open Big Picture. This uses the included `bigpicture_server.py`.

### On the PC

```powershell
python bigpicture_server.py
# listening on http://0.0.0.0:8765/bigpicture
```

Find the PC's LAN IP (`ipconfig` &rarr; IPv4 Address, e.g. `192.168.1.50`). Optionally
require a token so only you can trigger it:

```powershell
python bigpicture_server.py --token mysecret
```

To keep it running at login, point a Startup shortcut at `pythonw.exe
bigpicture_server.py` the same way `install.ps1` does for the watcher.

### On the iPhone

1. **Shortcuts** app &rarr; **+** &rarr; **Add Action** &rarr; **Get Contents of URL**.
2. Set the URL to `http://192.168.1.50:8765/bigpicture` (use your PC's IP; add
   `?token=mysecret` if you set one).
3. Name it "Big Picture" and add it to your Home Screen (share &rarr; Add to Home
   Screen) for one-tap access.

Tap it from the couch and Big Picture opens on the PC. You can also wire this into a
Bluetooth automation (Option 1, steps 2&ndash;5) if you have a *second* controller or
another Bluetooth device to trigger on.

> **Security note:** the server is meant for your home LAN and has no real auth beyond
> the optional shared token. Don't forward port 8765 to the internet.
