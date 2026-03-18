import logging
import subprocess
import os
import json
import time
from controllers.orchestrator import (
    SystemAuditOrchestrator,
    SystemAuditOrchestratorOptions,
)
from data import ScriptArguments
from helpers import run_as_admin, setup_logging


def get_config_from_file(config_file="config.json"):
    if not os.path.exists(config_file):
        return None

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config: dict[str, str | int] = json.load(f)

        # require URL at minimum
        if not config.get("target_url"):
            return None

        return ScriptArguments(**config)  # type: ignore

    except Exception as e:
        logging.error(f"Failed reading config: {e}")
        return None


def main():
    # Ensure Admin Privileges
    run_as_admin()

    # Check configuration file
    timeout = 300
    start_time = time.time()
    args: ScriptArguments | None = None
    while not args:
        args = get_config_from_file()

        if not args:
            if time.time() - start_time < timeout:
                time.sleep(5)
            else:
                logging.info(f"Timeout ({timeout}s): No configuration file detected.")
                return
    logging.info("Configuration file detected.")

    # Initialize Orchestrator
    paths = {
        "registry_exe": (
            args.regview_path
            if args.regview_path
            else "C:\\script\\RegistryChangesView.exe"
        ),
        "procmon_exe": (
            args.procmon_path if args.procmon_path else "C:\\script\\Procmon.exe"
        ),
        "tshark_exe": (
            args.tshark_path
            if args.tshark_path
            else "C:\\Program Files\\Wireshark\\tshark.exe"
        ),
    }
    options = SystemAuditOrchestratorOptions(
        **paths,
        iface_id=args.interface_num,
    )
    orchestrator = SystemAuditOrchestrator(
        base_output_dir=args.output_path, options=options
    )

    def browse_payload():
        edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
        cmd_path = edge_path if os.path.exists(edge_path) else "msedge"

        logging.info(f"🌐 Launching Microsoft Edge to: {args.target_url}")

        try:
            # Launch in new window and InPrivate for a clean audit
            subprocess.Popen([cmd_path, args.target_url, "--inprivate", "--new-window"])
            logging.info(f"⏳ Monitoring system activity for {args.duration}s...")
            time.sleep(args.duration)
        except Exception as e:
            logging.error(f"❌ Failed to launch browser: {e}")

    # 4. Execute
    orchestrator.run_audit(
        browse_payload,
        note=f"edge_audit_{args.target_url.split('//')[-1][:15]}",
        export_tshark_fields=args.tshark_fields,
    )

    signal_path = os.path.join(args.output_path, args.signal_file)
    with open(signal_path, "w") as f:
        f.write(f"Audit {args.target_url} completed.")
    logging.info(f"✅ Audit completed. Signal file created at: {signal_path}")


if __name__ == "__main__":
    setup_logging()
    main()
