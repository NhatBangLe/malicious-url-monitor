from dataclasses import dataclass
import os
import logging
from datetime import datetime
from typing import Callable, List, Optional

from controllers.procmon import ProcmonController
from controllers.registry import RegistryController
from controllers.tshark import TsharkController

_logger = logging.getLogger("AuditOrchestrator")


@dataclass
class SystemAuditOrchestratorOptions:
    registry_exe: str = "C:\\script\\RegistryChangesView.exe"
    procmon_exe: str = "C:\\script\\Procmon.exe"
    tshark_exe: str = "C:\\Program Files\\Wireshark\\tshark.exe"
    iface_id: int = 1


class SystemAuditOrchestrator:
    def __init__(self, base_output_dir, options: SystemAuditOrchestratorOptions):
        """
        Initializes the orchestration engine, creates timestamped output directories,
        and instantiates the specialized controllers for registry, process, and network auditing.

        Args:
            base_output_dir (str): The root folder where audit results will be stored.
                                   A new timestamped sub-folder is created for every run.
            options (SystemAuditOrchestratorOptions): A configuration dictionary defining executable locations and hardware IDs.
        """
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_path = os.path.abspath(os.path.join(base_output_dir, self.run_id))

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        # Initialize Controllers
        self.reg = RegistryController(exe_path=options.registry_exe)
        self.proc = ProcmonController(
            procmon_path=options.procmon_exe,
            output_path=self.output_path,
            log_name="procmon_log",
        )
        self.net = TsharkController(
            tshark_path=options.tshark_exe,
            output_path=self.output_path,
            interface_id=options.iface_id,
        )

    def run_audit(
        self,
        activity_callback: Callable[[], None],
        note: str = "",
        export_tshark_fields: Optional[List[str]] = None,
    ):
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
            _logger.info(f"Step 3/4: Monitoring system while doing activity...")
            activity_callback()  # This is where the user-defined activity takes place (e.g., opening an app, running a command, etc.)
            _logger.info(
                "Activity completed. Waiting for monitors to capture remaining data..."
            )

            # 4. Cleanup & Export
            _logger.info("Step 4/4: Stopping monitors and exporting data...")
            self.net.stop_capture()
            self.proc.stop_capture()

            # Final Registry Comparison (Live vs Snapshot)
            reg_csv = os.path.join(self.output_path, "registry_diff.csv")
            self.reg.compare_and_export(snapshot_dir, reg_csv)

            # Final Procmon Conversion
            self.proc.convert_to_csv()

            # Final TShark Conversion
            self.net.export_to_csv(fields=export_tshark_fields)

            _logger.info(
                f"--- ✅ Audit Complete! Logs saved to: {self.output_path} ---"
            )

        except Exception as e:
            _logger.error(f"❌ Audit failed during execution: {e}")
            # Emergency Stop
            self.proc.stop_capture()
            self.net.stop_capture()
