import subprocess
import csv
import logging
import time
from os import mkdir, path

_logger = logging.getLogger("RegistryController")

class RegistryController:
    """
    RegistryController utilizes NirSoft's RegistryChangesView to monitor and export Windows Registry changes.
    """
    def __init__(self, exe_path="RegistryChangesView.exe"):
        self.exe = path.abspath(exe_path)
        if not path.exists(self.exe):
            _logger.error(f"❌ RegistryChangesView executable not found at: {self.exe}")
            raise
        else:
            _logger.info(f"✅ RegistryController initialized with executable: {self.exe}")

    def capture_changes(self, duration_sec: int, output_dir_path: str, output_name="reg_diff"):
        """Captures current registry changes and exports to CSV."""
        _logger.info(f"🚀 Starting capture process. Duration: {duration_sec}s | Target: {output_dir_path}")
        
        snapshot_folder = path.abspath(path.join(output_dir_path, "reg_snapshot"))
        if not path.exists(snapshot_folder):
            mkdir(snapshot_folder)
            _logger.debug(f"✅ Created snapshot directory: {snapshot_folder}")
        
        self.create_snapshot(snapshot_folder)
        
        _logger.info(f"⏳ Snapshot created. Waiting {duration_sec} seconds for system changes...")
        time.sleep(duration_sec)
        
        export_path = path.join(output_dir_path, f'{output_name}.csv')
        self.compare_and_export(snapshot_folder, export_path)
        _logger.info("✅ Capture process complete.")

    def create_snapshot(self, folder_path: str):
        """Creates a registry snapshot in the specified folder."""
        _logger.info(f"⏳ Creating registry snapshot in: {folder_path}")
        cmd = [self.exe, "/CreateSnapshot", folder_path]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            _logger.info("✅ Snapshot successfully created.")
        except subprocess.CalledProcessError as e:
            _logger.error(f"❌ Failed to create snapshot. Error: {e.stderr.decode().strip()}")
            raise

    def compare_and_export(self, snapshot_path: str, output_csv: str):
        """Compares a snapshot to the current registry and exports to CSV."""
        _logger.info(f"⏳ Comparing snapshot at {snapshot_path} to live registry...")
        
        cmd = [
            self.exe,
            "/DataSourceType1", "2", "/RegSnapshotPath1", snapshot_path,
            "/DataSourceType2", "1",
            "/scomma", output_csv
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            _logger.info(f"✅ Comparison complete. Results exported to: {output_csv}")
        except subprocess.CalledProcessError as e:
            _logger.error(f"❌ Failed to export comparison. Error: {e.stderr.decode().strip()}")
            raise

    def get_changes(self, csv_file: str):
        """Parses the exported CSV into a list of dictionaries."""
        changes = []
        if not path.exists(csv_file):
            _logger.warning(f"⚠️ CSV file not found: {csv_file}")
            return changes

        try:
            # NirSoft tools typically export in UTF-16
            with open(csv_file, mode='r', encoding='utf-16') as f:
                reader = csv.DictReader(f)
                changes = [row for row in reader]
            
            _logger.info(f"✅ Successfully parsed {len(changes)} registry changes from CSV.")
        except Exception as e:
            _logger.error(f"❌ Error reading CSV file: {e}")
            
        return changes