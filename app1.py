import wmi
import time
import ctypes
import threading
import cv2
import datetime
import smtplib
from email.message import EmailMessage
import os

USB_LOGS_FOLDER = "USB_Logs_Insert"
VIDEO_LOGS_FOLDER = "logs_videos"

def detect_usb_insertion(lock_delay):
    c = wmi.WMI()
    query = "SELECT * FROM __InstanceCreationEvent WITHIN 2 WHERE TargetInstance ISA 'Win32_USBControllerDevice'"

    print("Monitoring USB events. Insert USB drive to lock the PC.")

    while True:
        watcher = c.watch_for(raw_wql=query)
        usb_inserted = False
        while not usb_inserted:
            event = watcher()
            if event:
                usb_inserted = True
                print("USB drive inserted.")
                usb_drive_label = get_usb_drive_label()
                log_usb_insertion(usb_drive_label)  # Log USB insertion with label
                lock_thread = threading.Thread(target=lock_pc_after_delay, args=(lock_delay,))
                lock_thread.start()
                capture_video_thread = threading.Thread(target=capture_video_after_lock)
                capture_video_thread.start()
                break

def lock_pc_after_delay(seconds):
    time.sleep(seconds)
    ctypes.windll.user32.LockWorkStation()

def capture_video_after_lock():
    # Access the webcam
    camera = cv2.VideoCapture(0)  # 0 for default webcam, change if needed

    # Define the codec
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # Get current date and time for the filename
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    video_filename = os.path.join(VIDEO_LOGS_FOLDER, f"captured_video_{current_time}.mp4")

    # Create a VideoWriter object with the filename including timestamp
    out = cv2.VideoWriter(video_filename, fourcc, 20.0, (640, 480))  # Adjust resolution if needed

    # Record a 5-second video
    start_time = time.time()
    while (time.time() - start_time) < 5:
        ret, frame = camera.read()
        if not ret:
            break
        out.write(frame)
        cv2.imshow('Recording...', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the resources
    camera.release()
    out.release()
    cv2.destroyAllWindows()

    # Send the captured video via email
    usb_drive_info = get_usb_drive_label()
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    email_content = f"USB Insertion Details:\nDate/Time: {current_datetime}\nUSB Drive Label: {usb_drive_info}\n\nPlease find the attached video recording for the same."
    send_email_with_video(video_filename, email_content)

def log_usb_insertion(usb_drive_label):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    log_filename = os.path.join(USB_LOGS_FOLDER, f"usb_insertions_{current_date}.txt")
    with open(log_filename, 'a') as file:
        log_entry = f"{datetime.datetime.now()} - USB Drive Inserted: {usb_drive_label}\n"
        file.write(log_entry)

def get_usb_drive_label():
    c = wmi.WMI()
    drives = c.Win32_Volume()
    usb_drives = [drive.Label for drive in drives if drive.DriveType == 2]  # Filter for removable drives
    return usb_drives[0] if usb_drives else "Unknown USB Drive"

def send_email_with_video(video_filename, content):
    sender_email = 'accesscyberspace@gmail.com'  # Replace with your email
    sender_password = 'yuypxxvcgktxfezu'     # Replace with your password
    receiver_email = 'accesscyberspace@gmail.com'  # Replace with recipient email

    msg = EmailMessage()
    msg['Subject'] = 'USB Inserted into your PC'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(content)

    with open(video_filename, 'rb') as file:
        video_data = file.read()
        msg.add_attachment(video_data, maintype='video', subtype='mp4', filename=os.path.basename(video_filename))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)

if __name__ == "__main__":
    if not os.path.exists(USB_LOGS_FOLDER):
        os.makedirs(USB_LOGS_FOLDER)
    if not os.path.exists(VIDEO_LOGS_FOLDER):
        os.makedirs(VIDEO_LOGS_FOLDER)
    detect_usb_insertion(1)  # Lock PC after 1 second of USB insertion
