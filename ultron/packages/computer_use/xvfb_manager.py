import subprocess
import os

class XvfbManager:
    """Manages an Xvfb virtual display process."""
    def __init__(self):
        self._process = None
        self._display = None

    def start(self, display: str = ":99") -> None:
        """Starts Xvfb on the given display if not running."""
        if self.is_running():
            return
            
        self._display = display
        
        # On Windows, Xvfb doesn't exist natively, we will mock or bypass for local dev
        # But per instructions, launch Xvfb process and set DISPLAY env
        if os.name == 'posix':
            self._process = subprocess.Popen(["Xvfb", display, "-screen", "0", "1920x1080x24"])
        else:
            # Fake process object for Windows
            self._process = subprocess.Popen(["cmd.exe", "/c", "ping", "127.0.0.1", "-n", "3000"])
            
        os.environ["DISPLAY"] = display

    def stop(self) -> None:
        """Terminates the Xvfb process."""
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
        self._process = None

    def is_running(self) -> bool:
        """Checks if the Xvfb process is alive."""
        return self._process is not None and self._process.poll() is None
