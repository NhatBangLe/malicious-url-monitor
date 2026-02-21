import subprocess
import os
import logging
import time
import argparse
from controllers.orchestrator import SystemAuditOrchestrator
from helpers import run_as_admin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Audit system changes while browsing via MS Edge.")
    
    # --- Core Audit Arguments ---
    parser.add_argument("url", help="The URL to browse.")
    parser.add_argument("--duration", type=int, default=30, help="Audit duration in seconds (default: 30)")
    parser.add_argument("--output", default="./Audit_Logs", help="Base directory for logs")

    # --- Tool Path Overrides ---
    # We use the existing paths as defaults so you don't have to type them every time
    parser.add_argument("--reg-path", 
                        default="C:\\tools\\RegistryChangesView.exe",
                        help="Path to RegistryChangesView.exe")
    
    parser.add_argument("--procmon-path", 
                        default="C:\\tools\Procmon.exe",
                        help="Path to Procmon.exe")
    
    parser.add_argument("--tshark-path", 
                        default="C:\\Program Files\\Wireshark\\tshark.exe",
                        help="Path to tshark.exe")
    
    parser.add_argument("--iface", type=int, default=1, 
                        help="TShark Interface ID (default: 1)")
    parser.add_argument("--tshark-fields", nargs='*', default=None,
                        help="Optional list of TShark fields to export (e.g., --tshark-fields frame.time ip.src ip.dst)")

    args = parser.parse_args()

    # 1. Ensure Admin Privileges
    run_as_admin()

    # 2. Map CLI arguments to the TOOL_PATHS dictionary
    TOOL_PATHS = {
        'registry_exe': args.reg_path,
        'procmon_exe': args.procmon_path,
        'tshark_exe': args.tshark_path,
        'iface_id': args.iface
    }

    # 3. Initialize Orchestrator with CLI-provided output dir
    orchestrator = SystemAuditOrchestrator(base_output_dir=args.output, paths=TOOL_PATHS)
    
    def browse_payload():
        edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
        cmd_path = edge_path if os.path.exists(edge_path) else "msedge"
        
        _logger.info(f"🌐 Launching Microsoft Edge to: {args.url}")
        
        try:
            # Launch in new window and InPrivate for a clean audit
            subprocess.Popen([cmd_path, args.url, "--inprivate", "--new-window"])
            _logger.info(f"⏳ Monitoring system activity for {args.duration}s...")
            time.sleep(args.duration)
        except Exception as e:
            _logger.error(f"❌ Failed to launch browser: {e}")

    # 4. Execute
    orchestrator.run_audit(browse_payload, 
                           note=f"edge_audit_{args.url.split('//')[-1][:15]}",
                           export_tshark_fields=args.tshark_fields)

if __name__ == "__main__":
    main()