# Turbo GIF - Zoom Browser Mode

Turbo GIF is a small Windows Tkinter desktop controller for sending one selected GIF into a Zoom meeting that is open in a web browser. The app is intentionally scoped to **Zoom Browser mode only**: it checks the active foreground window before it starts and keeps checking while it runs.

## What it does

- Lets you pick a local `.gif` file from a simple Tkinter UI.
- Copies the GIF to the Windows clipboard as a file attachment.
- Uses `F8` as a global start/stop hotkey.
- Sends `Ctrl+V`, waits for Zoom's preview, then sends `Enter`.
- Auto-stops if focus leaves a supported browser Zoom tab.

## Zoom Browser mode guard

The app only runs when the active foreground window matches both conditions:

1. The process is a supported browser:
   - Google Chrome (`chrome.exe`)
   - Microsoft Edge (`msedge.exe`)
   - Mozilla Firefox (`firefox.exe`)
   - Brave (`brave.exe`)
   - Opera (`opera.exe`)
   - Vivaldi (`vivaldi.exe`)
2. The active window title contains `Zoom`.

This blocks accidental posting into random apps, desktop chat clients, or the Zoom desktop client. If your browser or Zoom tab title is unusual, click **Re-check active window** after focusing the meeting tab to see the exact reason it is blocked.

## Requirements

- Windows 10 or Windows 11
- Python 3.10+
- A Zoom meeting opened in a supported browser
- A local GIF file

Tkinter ships with the standard Windows Python installer. If `python -m tkinter` fails, reinstall Python from <https://www.python.org/downloads/windows/> and keep the Tcl/Tk option enabled.

## Setup walkthrough

### 1. Clone or download the repo

```powershell
git clone git@github.com:KeeblerNubs/Turbo_gif.git
cd Turbo_gif
```

### 2. Create a virtual environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once for your user account:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the environment again.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Verify Tkinter opens

```powershell
python -m tkinter
```

A small Tk test window should appear. Close it before continuing.

### 5. Launch the app

```powershell
python TurboGifSpammer.py
```

## Daily usage

1. Open Zoom in Chrome, Edge, Firefox, Brave, Opera, or Vivaldi.
2. Join the meeting from the browser, not the Zoom desktop app.
3. Click inside the Zoom browser tab so it is the foreground window.
4. Start `TurboGifSpammer.py`.
5. Click **Browse for GIF** and choose a `.gif` file.
6. Set the delay between sends. The default is `0.5` seconds; use a higher value if Zoom or your network needs more time.
7. Press `F8` to start.
8. Press `F8` again to stop.

The app also stops itself if the active window is no longer a supported browser Zoom tab.

## Managing the desktop app

### Keep the app easy to launch

Create a `Start-TurboGif.ps1` file outside the repo or on your desktop:

```powershell
cd "C:\path\to\Turbo_gif"
.\.venv\Scripts\Activate.ps1
python TurboGifSpammer.py
```

Right-click the script and choose **Run with PowerShell** when you want to use the app.

### Update dependencies

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade -r requirements.txt
```

### Stop everything cleanly

- Press `F8` if the loop is running.
- Close the Tkinter window.
- If the global hotkey ever feels stuck, close the terminal window that launched the app.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `Start blocked: this only runs in Zoom Browser mode.` | Focus the Zoom meeting tab in a supported browser and click **Re-check active window**. |
| The active app says `Zoom.exe`. | You are in the Zoom desktop client. Join from the browser instead. |
| `ModuleNotFoundError` for `keyboard`, `psutil`, or `win32clipboard`. | Activate the virtual environment and run `python -m pip install -r requirements.txt`. |
| `python -m tkinter` fails. | Reinstall Python with Tcl/Tk enabled. |
| GIF pastes but does not send. | Increase the delay so Zoom has enough time to stage the attachment preview. |

## Project layout

```text
TurboGifSpammer.py  # Tkinter app and Zoom Browser mode guard
requirements.txt   # Python runtime dependencies
README.md          # Setup, usage, and management walkthrough
```

## Safety notes

Use this only where automated posting is allowed and welcome. The browser guard prevents many accidents, but it cannot decide whether a meeting is appropriate for automation. That part is still on the operator.
