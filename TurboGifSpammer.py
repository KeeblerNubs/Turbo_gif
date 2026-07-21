"""Tkinter desktop controller for sending one selected GIF in Zoom browser mode.

The app intentionally refuses to run unless the active foreground window appears to
be a Zoom meeting opened in a supported web browser. That guard keeps the tool
scoped to the intended Zoom Browser mode workflow instead of pasting into random
apps or the Zoom desktop client.
"""

from __future__ import annotations

import os
import struct
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

if sys.platform == "win32":
    import keyboard
    import psutil
    import win32clipboard
    import win32gui
    import win32process
else:
    keyboard = None
    psutil = None
    win32clipboard = None
    win32gui = None
    win32process = None

APP_TITLE = "Turbo GIF - Zoom Browser Mode"
DEFAULT_DELAY_SECONDS = 0.5
PREVIEW_BUFFER_SECONDS = 0.3
HOTKEY = "F8"
SUPPORTED_BROWSER_PROCESSES = {
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
    "brave.exe",
    "opera.exe",
    "vivaldi.exe",
}


class GifControllerApp:
    """Small Tkinter UI that manages GIF selection and guarded paste loops."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("520x390")
        self.root.minsize(520, 390)
        self.root.attributes("-topmost", True)

        self.gif_path: Path | None = None
        self.is_running = False
        self.worker: threading.Thread | None = None
        self.status_var = tk.StringVar(value="Select a GIF, focus Zoom in your browser, then press F8.")
        self.target_var = tk.StringVar(value="Target check pending...")
        self.file_var = tk.StringVar(value="No GIF selected")
        self.delay_var = tk.StringVar(value=str(DEFAULT_DELAY_SECONDS))

        self._build_ui()
        assert keyboard is not None
        keyboard.on_press_key(HOTKEY, self.toggle_runner, suppress=True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.refresh_target_status()

    def _build_ui(self) -> None:
        wrapper = tk.Frame(self.root, padx=18, pady=16)
        wrapper.pack(fill=tk.BOTH, expand=True)

        tk.Label(wrapper, text=APP_TITLE, font=("Arial", 16, "bold")).pack(anchor="w")
        tk.Label(
            wrapper,
            text="Guarded desktop controller for Zoom meetings running in a web browser only.",
            wraplength=470,
            justify=tk.LEFT,
        ).pack(anchor="w", pady=(4, 12))

        tk.Button(wrapper, text="Browse for GIF", command=self.browse_file, font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Label(wrapper, textvariable=self.file_var, fg="green", wraplength=470, justify=tk.LEFT).pack(anchor="w", pady=(6, 12))

        delay_row = tk.Frame(wrapper)
        delay_row.pack(fill=tk.X, pady=(0, 12))
        tk.Label(delay_row, text="Delay between sends (seconds):").pack(side=tk.LEFT)
        tk.Entry(delay_row, width=8, textvariable=self.delay_var).pack(side=tk.LEFT, padx=8)

        tk.Label(wrapper, text="Required target", font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Label(wrapper, textvariable=self.target_var, fg="purple", wraplength=470, justify=tk.LEFT).pack(anchor="w", pady=(4, 10))
        tk.Button(wrapper, text="Re-check active window", command=self.refresh_target_status).pack(anchor="w", pady=(0, 12))

        tk.Label(wrapper, textvariable=self.status_var, fg="blue", font=("Arial", 11, "bold"), wraplength=470).pack(
            anchor="w", pady=(4, 12)
        )
        tk.Label(
            wrapper,
            text="Hotkey: F8 starts/stops. The loop auto-stops if focus leaves a supported browser Zoom tab.",
            wraplength=470,
            justify=tk.LEFT,
        ).pack(anchor="w")

    def browse_file(self) -> None:
        filepath = filedialog.askopenfilename(title="Select a GIF", filetypes=[("GIF files", "*.gif")])
        if not filepath:
            return

        self.gif_path = Path(filepath).resolve()
        self.file_var.set(str(self.gif_path))
        self.copy_file_to_clipboard()
        self.status_var.set("GIF loaded. Focus your Zoom browser meeting and press F8.")

    def copy_file_to_clipboard(self) -> None:
        if not self.gif_path:
            return

        offset = struct.calcsize("5I")
        files = os.fspath(self.gif_path) + "\0\0"
        data = struct.pack("5I", offset, 0, 0, 0, 1) + files.encode("utf-16le")

        assert win32clipboard is not None
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_HDROP, data)
        finally:
            win32clipboard.CloseClipboard()

    def get_target_status(self) -> tuple[bool, str]:
        assert psutil is not None
        assert win32gui is not None
        assert win32process is not None
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd).strip()
        if not hwnd or not title:
            return False, "No active foreground window detected."

        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process_name = psutil.Process(pid).name().lower()
        is_browser = process_name in SUPPORTED_BROWSER_PROCESSES
        has_zoom_title = "zoom" in title.lower()

        if is_browser and has_zoom_title:
            return True, f"Ready: '{title}' in {process_name}."
        if not is_browser:
            return False, f"Blocked: active app is {process_name}, not a supported browser."
        return False, f"Blocked: browser tab title does not look like Zoom ('{title}')."

    def refresh_target_status(self) -> bool:
        ready, details = self.get_target_status()
        self.target_var.set(details)
        return ready

    def parse_delay(self) -> float:
        try:
            delay = float(self.delay_var.get())
        except ValueError:
            delay = DEFAULT_DELAY_SECONDS
            self.delay_var.set(str(DEFAULT_DELAY_SECONDS))
        return max(0.2, delay)

    def toggle_runner(self, event: object | None = None) -> None:
        if self.is_running:
            self.stop_runner("Stopped. Focus Zoom in your browser and press F8 to start again.")
            return

        if not self.gif_path:
            self.status_var.set("Choose a GIF before starting.")
            return
        if not self.refresh_target_status():
            self.status_var.set("Start blocked: this only runs in Zoom Browser mode.")
            return

        self.copy_file_to_clipboard()
        self.is_running = True
        self.status_var.set("Running for Zoom Browser mode. Press F8 to stop.")
        self.worker = threading.Thread(target=self.run_loop, args=(self.parse_delay(),), daemon=True)
        self.worker.start()

    def stop_runner(self, message: str) -> None:
        self.is_running = False
        self.status_var.set(message)

    def run_loop(self, delay: float) -> None:
        while self.is_running:
            ready, details = self.get_target_status()
            self.root.after(0, self.target_var.set, details)
            if not ready:
                self.root.after(0, self.stop_runner, "Auto-stopped: focus left Zoom Browser mode.")
                break

            assert keyboard is not None
            keyboard.send("ctrl+v")
            time.sleep(PREVIEW_BUFFER_SECONDS)
            if not self.is_running:
                break
            keyboard.send("enter")
            time.sleep(delay)

    def close(self) -> None:
        self.is_running = False
        if keyboard is not None:
            keyboard.unhook_all()
        self.root.destroy()


def ensure_windows() -> None:
    if sys.platform != "win32":
        messagebox.showerror(APP_TITLE, "This app uses the Windows clipboard and keyboard APIs. Run it on Windows.")
        raise SystemExit(1)


if __name__ == "__main__":
    ensure_windows()
    root = tk.Tk()
    app = GifControllerApp(root)
    root.mainloop()
