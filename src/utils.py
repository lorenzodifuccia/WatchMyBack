import os
import sys
import time
import logging
import threading


class ThreadWatchdog:
    def __init__(self, name, instance, *args, **kwargs):
        self.name = name
        self.instance = instance
        self.args = args
        self.kwargs = kwargs

        self.thread = None
        self.watchdog_thread = False
        self.running = False

        self.logger = logging.getLogger(self.name + ".watchdog")

    def start(self):
        self.logger.info("Starting!")
        self.running = True

        self.thread = threading.Thread(name=self.name, target=self.instance.start, *self.args, **self.kwargs)
        self.thread.start()

    def start_with_watchdog(self):
        self.start()
        self.watchdog_thread = threading.Thread(name=self.name + ".watchdog", target=self.watchdog)
        self.watchdog_thread.start()

    def kill(self):
        self.logger.info("Killing!")
        self.running = False
        self.instance.stop()

    def watchdog(self):
        last_error = False
        error_counter = 0
        while self.running:
            time.sleep(1)

            if time.time() > last_error + 60:
                error_counter = 0

            if not self.thread.is_alive() and self.running:
                error_counter += 1
                last_error = time.time()

                if error_counter > 5:
                    self.logger.error("Too many error! Killing...")
                    self.kill()
                    break

                self.logger.error("Error in %s, trying restarting..." % self.name)
                time.sleep(2 * error_counter)
                self.start()


def show_notification(title, message):
    if sys.platform == "darwin":
        os.system(f"""osascript -e 'display notification "{message}" with title "{title}"' &""")

    elif sys.platform == "win32":
        pass

    else:
        pass


def lock_screen():
    if sys.platform == "darwin":
        os.system("""osascript -e 'tell application "Finder" to sleep'""")

    elif sys.platform == "win32":
        pass

    else:
        pass


def reset_camera_permission():
    if sys.platform == "darwin":
        os.system("tccutil reset Camera")

    elif sys.platform == "win32":
        pass

    else:
        pass
