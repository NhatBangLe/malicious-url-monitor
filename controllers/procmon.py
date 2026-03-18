import subprocess
import time
import logging
from os import path, remove


class ProcmonController:
    """
    ProcmonController manages Sysinternals Process Monitor to capture system activity.
    """

    def __init__(self, procmon_path: str, output_path: str, log_name="log"):
        self._logger = logging.getLogger("ProcmonController")
        self.procmon = path.abspath(procmon_path)
        self.pml_file = path.abspath(path.join(output_path, f"{log_name}.PML"))
        self.csv_file = path.abspath(path.join(output_path, f"{log_name}.CSV"))

        if not path.exists(self.procmon):
            self._logger.error(f"Procmon executable not found at: {self.procmon}")
        else:
            self._logger.info(f"ProcmonController initialized. Binary: {self.procmon}")

    def capture(
        self, duration_sec: int, convert_to_csv: bool = True, cleanup: bool = False
    ):
        """
        Executes a full capture cycle.
        """
        self._logger.info(f"Starting Procmon capture cycle for {duration_sec} seconds.")
        self.start_capture()

        self._logger.info(f"Recording in progress...")
        time.sleep(duration_sec)

        self.stop_capture()

        if convert_to_csv:
            success = self.convert_to_csv()
            if success and cleanup:
                self.cleanup_pml()

        self._logger.info("Capture cycle finished.")

    def start_capture(self):
        """Launches the Procmon process in the background."""
        self._logger.info("🚀 Launching Procmon (background)...")
        try:
            # /AcceptEula ensures no hidden popups block the process
            subprocess.Popen(
                [
                    self.procmon,
                    "/AcceptEula",
                    "/BackingFile",
                    self.pml_file,
                    "/Quiet",
                    "/Minimized",
                ]
            )
        except Exception as e:
            self._logger.error(f"Failed to launch Procmon: {e}")
            raise

    def stop_capture(self):
        """Signals Procmon to terminate and waits for the log file to be released."""
        self._logger.info("🛑 Stopping Procmon capture...")
        try:
            subprocess.run(
                [self.procmon, "/Terminate"], check=True, capture_output=True
            )
        except subprocess.CalledProcessError as e:
            self._logger.error(f"Error during Procmon termination: {e}")

        # CRITICAL: Wait until the .pml file is actually written and released
        self._logger.info("⏳ Waiting for file handle release and disk flush...")
        timeout = 10
        file_ready = False
        while timeout > 0:
            if path.exists(self.pml_file) and path.getsize(self.pml_file) > 0:
                time.sleep(2)  # Extra padding for final disk flush
                file_ready = True
                break
            time.sleep(1)
            timeout -= 1

        if file_ready:
            self._logger.info(f"✅ Log file stabilized: {self.pml_file}")
        else:
            self._logger.warning(
                f"⚠️ Timeout reached: Log file {self.pml_file} may be incomplete or missing."
            )

    def convert_to_csv(self) -> bool:
        """Converts the binary PML file to a readable CSV."""
        if not path.exists(self.pml_file):
            self._logger.error(
                f"❌ Conversion aborted: {self.pml_file} does not exist."
            )
            return False

        self._logger.info(f"📄 Converting {self.pml_file} to CSV format...")
        try:
            subprocess.run(
                [
                    self.procmon,
                    "/OpenLog",
                    self.pml_file,
                    "/SaveAs",
                    self.csv_file,
                    "/Quiet",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            if path.exists(self.csv_file):
                self._logger.info(f"✅ Success! CSV saved to: {self.csv_file}")
                return True
            else:
                self._logger.error(
                    "❌ Conversion failed: Procmon exited but CSV was not created."
                )
                return False
        except subprocess.CalledProcessError as e:
            self._logger.error(f"❌ Subprocess error during conversion: {e}")
            return False

    def cleanup_pml(self):
        """Deletes the large binary .PML file to save disk space."""
        if path.exists(self.pml_file):
            try:
                remove(self.pml_file)
                self._logger.info(f"🧹 Cleaned up binary file: {self.pml_file}")
            except OSError as e:
                self._logger.warning(f"⚠️ Could not delete {self.pml_file}: {e}")
