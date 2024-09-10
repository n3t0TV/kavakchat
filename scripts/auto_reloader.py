import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

'''
Runs Server script and restarts if changes are done to the code
'''

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.start_script()

    def start_script(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen(['python', self.script])

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f'{event.src_path} modified; restarting server...')
            self.start_script()

if __name__ == "__main__":
    script_to_watch = "server.py"
    event_handler = ChangeHandler(script_to_watch)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()