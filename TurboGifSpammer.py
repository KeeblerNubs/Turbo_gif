import tkinter as tk
from tkinter import filedialog
import threading
import time
import keyboard
import win32clipboard
import struct
import os
import sys

class GifSpammerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Turbo GIF Spammer")
        self.root.geometry("400x250")
        self.root.attributes("-topmost", True)

        self.gif_path = None
        self.is_spamming = False
        self.spam_thread = None

        self.label = tk.Label(root, text="Select a GIF to spam:", font=("Arial", 10))
        self.label.pack(pady=10)

        self.browse_btn = tk.Button(root, text="Browse for GIF", command=self.browse_file, font=("Arial", 10, "bold"))
        self.browse_btn.pack(pady=5)

        self.file_label = tk.Label(root, text="No file selected", fg="red")
        self.file_label.pack(pady=5)

        self.speed_frame = tk.Frame(root)
        self.speed_frame.pack(pady=10)

        self.speed_label = tk.Label(self.speed_frame, text="Delay between loops (sec):")
        self.speed_label.pack(side=tk.LEFT, padx=5)

        self.speed_entry = tk.Entry(self.speed_frame, width=8)
        self.speed_entry.insert(0, "0.5")
        self.speed_entry.pack(side=tk.LEFT)

        self.info_label = tk.Label(root, text="Press F8 to Start/Stop", fg="blue", font=("Arial", 12, "bold"))
        self.info_label.pack(pady=15)

        # Bind global hotkey
        keyboard.on_press_key("F8", self.toggle_spam, suppress=True)

    def browse_file(self):
        filepath = filedialog.askopenfilename(
            title="Select a GIF",
            filetypes=[("GIF Files", "*.gif"), ("All Files", "*.*")]
        )
        if filepath:
            self.gif_path = os.path.normpath(filepath)
            self.file_label.config(text=os.path.basename(self.gif_path), fg="green")
            self.copy_file_to_clipboard()

    def copy_file_to_clipboard(self):
        if not self.gif_path:
            return

        # Create DROPFILES struct to simulate native Windows file copy (CF_HDROP)
        offset = struct.calcsize("5I")
        files = self.gif_path + '\0\0'
        data = struct.pack("5I", offset, 0, 0, 0, 1) + files.encode("utf-16le")

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_HDROP, data)
        win32clipboard.CloseClipboard()

    def toggle_spam(self, event=None):
        if not self.gif_path:
            print("No GIF selected!")
            return

        self.is_spamming = not self.is_spamming

        if self.is_spamming:
            self.info_label.config(text="SPAMMING! Press F8 to Stop", fg="red")
            self.copy_file_to_clipboard() # Ensure it's in the clipboard before we start

            try:
                delay = float(self.speed_entry.get())
            except ValueError:
                delay = 0.5

            # Run spam loop in a background daemon thread to prevent freezing Tkinter
            self.spam_thread = threading.Thread(target=self.spam_loop, args=(delay,))
            self.spam_thread.daemon = True
            self.spam_thread.start()
        else:
            self.info_label.config(text="Press F8 to Start/Stop", fg="blue")

    def spam_loop(self, delay):
        while self.is_spamming:
            keyboard.send("ctrl+v")
            time.sleep(0.3) # Short buffer to let Discord/Teams stage the file preview
            
            if not self.is_spamming:
                break
                
            keyboard.send("enter")
            time.sleep(delay)

if __name__ == "__main__":
    root = tk.Tk()
    app = GifSpammerApp(root)
    root.mainloop()
