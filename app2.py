import os
import ctypes
import time
from string import ascii_uppercase
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import win32api

class USBFileEventHandler(FileSystemEventHandler):
    def __init__(self, excluded_drive, log_file):
        super().__init__()
        self.excluded_drive = excluded_drive
        self.log_file = log_file

    def on_any_event(self, event):
        if event.src_path.startswith(self.excluded_drive):
            return

        usb_device = win32api.GetVolumeInformation(os.path.splitdrive(event.src_path)[0])[0]
        log_message = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - File system event detected on USB drive '{usb_device}': {event.event_type}, Path: {event.src_path}\n"
        print(log_message)

        with open(self.log_file, 'a') as f:
            f.write(log_message)

        print("Locking PC...")
        ctypes.windll.user32.LockWorkStation()

def get_removable_drives():
    return [f"{d}:\\" for d in ascii_uppercase if os.path.exists(f"{d}:") and os.path.ismount(f"{d}:") and d != 'C']

if __name__ == "__main__":
    log_directory = "USB_Logs"
    os.makedirs(log_directory, exist_ok=True)

    while True:
        current_date = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_directory, f"USB_Log_{current_date}.txt")

        existing_drives = get_removable_drives()
        event_handlers = []
        observers = []

        for drive in existing_drives:
            event_handler = USBFileEventHandler(excluded_drive='C:\\', log_file=log_file)
            observer = Observer()
            observer.schedule(event_handler, path=drive, recursive=True)
            observer.start()

            event_handlers.append(event_handler)
            observers.append(observer)

            usb_device = win32api.GetVolumeInformation(os.path.splitdrive(drive)[0])[0]
            #print(f"Monitoring file events on '{usb_device}' ({drive}). Locking PC upon modifications.")

        # Check for new drives every 10 seconds (adjust as needed)
        time.sleep(10)

        # Stop and join observers for existing drives
        for obs in observers:
            obs.stop()
            obs.join()
