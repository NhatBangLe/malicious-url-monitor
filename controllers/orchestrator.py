import os
import time
import logging
from datetime import datetime

from controllers.procmon import ProcmonController
from controllers.registry import RegistryController
from controllers.tshark import TsharkController

_logger = logging.getLogger("AuditOrchestrator")

class SystemAuditOrchestrator:
    def __init__(self, base_output_dir, paths: dict):
        """
        Initializes the orchestration engine, creates timestamped output directories, 
        and instantiates the specialized controllers for registry, process, and network auditing.

        Args:
            base_output_dir (str): The root folder where audit results will be stored. 
                                   A new timestamped sub-folder is created for every run.
            paths (dict): A configuration dictionary defining executable locations and hardware IDs.
                Required Keys:
                    - **'registry_exe'** (str): Absolute path to 'RegistryChangesView.exe'.
                    - **'procmon_exe'** (str): Absolute path to 'Procmon.exe' or 'Procmon64.exe'.
                    - **'tshark_exe'** (str): Absolute path to 'tshark.exe'.
                Optional Keys:
                    - **'iface_id'** (int): The numeric ID of the network interface to capture. 
                                            Defaults to 1 if not provided.
        """
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_path = os.path.abspath(os.path.join(base_output_dir, self.run_id))
        
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        # Initialize Controllers
        self.reg = RegistryController(paths['registry_exe'])
        self.proc = ProcmonController(paths['procmon_exe'], self.output_path, "procmon_log")
        self.net = TsharkController(paths['tshark_exe'], self.output_path, interface_id=paths.get('iface_id', 1))

    def run_audit(self, duration_sec: int, note: str | None = "activity_audit"):
        _logger.info(f"--- 🚀 Starting Unified Audit: {note} (ID: {self.run_id}) ---")
        
        try:
            # 1. Baseline: Capture Registry state BEFORE activity
            _logger.info("Step 1/4: Capturing Registry Baseline...")
            snapshot_dir = os.path.join(self.output_path, "reg_snapshot_before")
            self.reg.create_snapshot(snapshot_dir)

            # 2. Start Live Monitors
            _logger.info("Step 2/4: Starting Procmon and TShark...")
            self.proc.start_capture()
            self.net.start_capture()

            # 3. Wait for the event/activity
            _logger.info(f"Step 3/4: Monitoring system for {duration_sec} seconds...")
            time.sleep(duration_sec)

            # 4. Cleanup & Export
            _logger.info("Step 4/4: Stopping monitors and exporting data...")
            self.net.stop_capture()
            self.proc.stop_capture()
            
            # Final Registry Comparison (Live vs Snapshot)
            reg_csv = os.path.join(self.output_path, "registry_diff.csv")
            self.reg.compare_and_export(snapshot_dir, reg_csv)
            
            # Final Procmon Conversion
            self.proc.convert_to_csv()
            self.net.export_to_csv()

            _logger.info(f"--- ✅ Audit Complete! Logs saved to: {self.output_path} ---")

        except Exception as e:
            _logger.error(f"❌ Audit failed during execution: {e}")
            # Emergency Stop
            self.proc.stop_capture()
            self.net.stop_capture()