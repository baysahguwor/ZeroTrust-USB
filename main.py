import subprocess
import pystray
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image

def start_scripts():
    # Launch the scripts in a hidden window
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    script1_process = subprocess.Popen(["python", "app1.py"], startupinfo=startupinfo)  # Start script1.py
    script2_process = subprocess.Popen(["python", "app2.py"], startupinfo=startupinfo)  # Start script2.py
    return script1_process, script2_process

def stop_scripts(script1_process, script2_process):
    script1_process.terminate()
    script2_process.terminate()

def on_start_clicked(icon, item):
    global script1, script2
    script1, script2 = start_scripts()

def on_stop_clicked(icon, item):
    global script1, script2
    stop_scripts(script1, script2)

def on_exit_clicked(icon, item):
    global script1, script2
    if script1 and script2:
        stop_scripts(script1, script2)
    icon.stop()

def setup_system_tray():
    image = Image.open("icon1.png")  # Replace with your icon path

    menu = Menu(
        MenuItem('Start Scripts', on_start_clicked),
        MenuItem('Stop Scripts', on_stop_clicked),
        MenuItem('Exit', on_exit_clicked)
    )

    icon = Icon("Script Controller", image, "Script Controller", menu)

    # Hide the main window when the script starts
    icon.visible = False

    icon.run()

if __name__ == "__main__":
    script1, script2 = None, None  # Initialize script processes as None

    setup_system_tray()
