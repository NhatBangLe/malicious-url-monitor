import logging
import time
from controllers.orchestrator import SystemAuditOrchestrator
from helpers import run_as_admin


# Configure logging to show time, level, and message
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    run_as_admin()

    TOOL_PATHS = {
        'registry_exe': "C:\\tools\RegistryChangesView.exe",
        'procmon_exe': "C:\\Tools\Procmon64.exe",
        'tshark_exe': "C:\Program Files\Wireshark\tshark.exe",
        'iface_id': 1  # Use tshark -D to find your interface ID
    }

    orchestrator = SystemAuditOrchestrator(base_output_dir="./Audit_Logs", paths=TOOL_PATHS)
    
    # Run the audit for 30 seconds
    orchestrator.run_audit(duration_sec=30, note="Software_Installer_Test")