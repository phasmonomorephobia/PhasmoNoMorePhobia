
import sys
import time
import subprocess
import threading

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# Project paths
ROOT = Path(__file__).resolve().parent
APP = ROOT / "src" / "main.py"
WATCH_DIR = ROOT / "src"

# Application process
process = None
restart_timer = None
process_lock = threading.Lock()
restart_lock = threading.Lock()


def start_app():
    global process

    with process_lock:
        print("\n[DEV] Starting PhasmoNoMorePhobia...")

        process = subprocess.Popen(
            [sys.executable, str(APP)],
            cwd=ROOT
        )


def stop_app():
    global process

    with process_lock:
        if process and process.poll() is None:
            print("[DEV] Closing application...")

            process.terminate()

            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()

        process = None


def restart_app():
    stop_app()
    time.sleep(0.3)
    start_app()


class ChangeHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        global restart_timer

        if event.is_directory:
            return

        # Only restart when a Python file changes
        paths = [event.src_path]

        if event.event_type == "moved":
            paths.append(event.dest_path)

        if not any(str(path).endswith(".py") for path in paths):
            return

        global_lock = threading.Lock()

        with restart_lock:
            if restart_timer is not None:
                restart_timer.cancel()

            restart_timer = threading.Timer(
                0.7,
                restart_app
            )

            restart_timer.start()


def main():
    observer = Observer()

    handler = ChangeHandler()

    observer.schedule(
        handler,
        str(WATCH_DIR),
        recursive=True
    )

    observer.start()

    print("===================================")
    print(" PhasmoNoMorePhobia Development")
    print(" Automatic Reload Enabled")
    print("===================================")
    print("Save a Python file to reload.")
    print("Press CTRL+C to stop.\n")

    start_app()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[DEV] Shutting down...")

        if restart_timer is not None:
            restart_timer.cancel()

        observer.stop()
        stop_app()

    observer.join()


if __name__ == "__main__":
    main()
