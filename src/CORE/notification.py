from win10toast import ToastNotifier

class Notification:
    def __init__(self,):
        self.toast = ToastNotifier()
        print("Notification system initialized.")
    def Notify(self, title, message, duration=10, icon_path=r"G:\My Drive\Project - ChronoLOG\assets\AppIcon.ico"):
        self.title = title
        self.message = message
        self.duration = duration
        self.icon_path = icon_path
        self.toast.show_toast(self.title, self.message, duration=self.duration, icon_path=self.icon_path)

Notification = Notification()
Notification.Notify("ChronoLOG", "This is a test notification from ChronoLOG.")

# import subprocess
# import time
# from threading import Thread

# class NotificationManager:
#     def __init__(self):
#         self.running = True
#         self.thread = Thread(target=self.run, daemon=True)
#         print("NotificationManager started.")

#     def start(self):
#         self.thread.start()
#         print("NotificationManager is running.")

#     def stop(self):
#         self.running = False
#         print("NotificationManager stopped.")

#     def show_toast(title, message):
#         ps_script = f'''
#         Import-Module BurntToast
#         New-BurntToastNotification -Text "{title}", "{message}"
#         '''
#         subprocess.run(["powershell", "-Command", ps_script], shell=True)

#         print(f"Notification shown: {title} - {message}")

#     def run(self):
#         while self.running:
#             # For demo: Notify every 15 seconds
#             self.show_toast("ChronoLOG", "Session starts in 10 minutes!")
#             time.sleep(15)  # adjust as needed

# if __name__ == "__main__":
#     notifier = NotificationManager()
#     notifier.start()

#     try:
#         while True:
#             time.sleep(1)  # keep main thread alive
#     except KeyboardInterrupt:
#         notifier.stop()
