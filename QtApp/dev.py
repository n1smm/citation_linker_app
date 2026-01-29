import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
  def __init__(self, command):
      self.command = command
      self.process = None
      self.restart()

  def on_modified(self, event):
      if event.src_path.endswith('.py'):
          print(f"\n🔄 Detected change in {event.src_path}")
          self.restart()

  def restart(self):
      if self.process:
          print("⏹️  Stopping app...")
          self.process.terminate()
          self.process.wait()

      print("▶️  Starting app...")
      self.process = subprocess.Popen(self.command)

  def stop(self):
      if self.process:
          self.process.terminate()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]    
    else:
        file_path = None
        
    src_path = Path(__file__).parent / "src"
    command = [sys.executable, "-m", "qtapp.dev"]
    if file_path:
        command.append(file_path)

    handler = RestartHandler(command)
    observer = Observer()
    observer.schedule(handler, str(src_path), recursive=True)
    observer.start()

    print(f"👀 Watching {src_path} for changes...")
    print("Press Ctrl+C to stop")

    try:
      while True:
          time.sleep(1)
    except KeyboardInterrupt:
      handler.stop()
      observer.stop()

    observer.join()
