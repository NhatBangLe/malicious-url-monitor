import subprocess
import logging
from enum import Enum
from typing import List, Optional


class BrowserType(Enum):
    CHROME = "chrome"
    EDGE = "edge"


class BrowserController:
    """
    Controls browser lifecycle by opening URLs and closing browser instances.
    Supports Chrome, and Edge.
    """

    BROKER_PATHS = {
        BrowserType.CHROME: r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        BrowserType.EDGE: r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    }

    def __init__(self, type: BrowserType = BrowserType.CHROME):
        """
        Initializes the BrowserController.

        Args:
            type (BrowserType): The browser to control. Defaults to Chrome.
        """
        self.type = type
        self._logger = logging.getLogger(__name__)
        self.opened_url: Optional[str] = None
        self._process: Optional[subprocess.Popen[bytes]] = None

    def open_url(self, url: str) -> bool:
        """
        Opens a URL in the specified browser.

        Args:1
            url (str): The URL to open.

        Returns:
            bool: True if the browser was launched successfully, False otherwise.
        """
        browser_path = self.BROKER_PATHS.get(self.type)
        if not browser_path:
            self._logger.error(f"No path configured for browser: {self.type}")
            return False

        cmd = self._build_open_command(browser_path, url)
        self.opened_url = url
        self._logger.debug(f"Executing: {' '.join(cmd)}")

        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._logger.info(f"Opened {self.type.value} with URL: {url}")
            return True
        except FileNotFoundError:
            self._logger.error(f"Browser executable not found at: {browser_path}")
            return False
        except Exception as e:
            self._logger.error(f"Failed to open browser: {e}")
            return False

    def close(self) -> bool:
        """
        Closes the browser instance opened by this controller.

        Returns:
            bool: True if the browser was closed successfully, False otherwise.
        """
        if not self._process:
            self._logger.warning("No browser process to close")
            return False

        try:
            self._process.terminate()
            self._process.wait(timeout=10)
            self._logger.info(f"Closed {self.type.value}")
            return True
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._logger.warning(f"Force-killed {self.type.value}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to close browser: {e}")
            return False
        finally:
            self._process = None

    def _build_open_command(self, browser_path: str, url: str) -> List[str]:
        """
        Builds the command to open a URL in the specified browser.

        Args:
            browser_path (str): Path to the browser executable.
            url (str): The URL to open.

        Returns:
            list[str]: The command arguments list.
        """
        if self.type in (BrowserType.CHROME, BrowserType.EDGE):
            return [browser_path,
                    "--new-window",
                    "--allow-running-insecure-content",
                    "--disable-web-security",
                    "--disable-site-isolation-trials",
                    "--no-sandbox",
                    "--no-first-run",
                    "--disable-popup-blocking",
                    "--disable-features=HttpsUpgrades,AutoupgradeInsecureRequests,HttpsOnlyMode,EdgeAutomaticHttps",
                    f"--unsafely-treat-insecure-origin-as-secure={url}", 
                    url]
        return [browser_path, url]
