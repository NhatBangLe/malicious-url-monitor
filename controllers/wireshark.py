import subprocess
import logging
from os import path

_logger = logging.getLogger("TsharkController")

class TsharkController:
    """
    TsharkController manages TShark (Wireshark CLI) to capture and analyze network traffic.
    """
    def __init__(self, tshark_path: str, output_path: str, interface_id: int = 1):
        self.tshark = path.abspath(tshark_path)
        self.output_dir = path.abspath(output_path)
        self.interface_id = interface_id
        self.pcap_file = path.abspath(path.join(output_path, "capture.pcapng"))
        self._process: subprocess.Popen = None

        if not path.exists(self.tshark):
            _logger.error(f"❌ TShark executable not found at: {self.tshark}")
        else:
            _logger.info(f"✅ TsharkController initialized. Interface ID: {self.interface_id}")

    def list_interfaces(self):
        """Prints available network interfaces to help identify the correct ID."""
        _logger.info("⏳ Listing available network interfaces...")
        try:
            result = subprocess.run([self.tshark, "-D"], capture_output=True, text=True, check=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            _logger.error(f"❌ Could not list interfaces: {e}")

    def start_capture(self, capture_filter: str = ""):
        """Starts a background capture process."""
        _logger.info("🌐 Starting TShark capture...")
        
        # -i: Interface ID
        # -w: Write to file
        # -f: Capture filter (e.g., "tcp port 80")
        cmd = [self.tshark, "-i", str(self.interface_id), "-w", self.pcap_file]
        if capture_filter:
            cmd.extend(["-f", capture_filter])

        try:
            # We use Popen so it runs in the background
            self._process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            _logger.info(f"✅ Capture started (PID: {self._process.pid}). Saving to {self.pcap_file}")
        except Exception as e:
            _logger.error(f"❌ Failed to start TShark: {e}")

    def stop_capture(self):
        """Stops the TShark process gracefully."""
        if self._process:
            _logger.info("🛑 Stopping TShark capture...")
            # TShark needs a graceful SIGTERM to finalize the pcap file header
            self._process.terminate()
            try:
                self._process.wait(timeout=10) # 10 seconds timeout 
                _logger.info("✅ Capture stopped and file finalized.")
            except subprocess.TimeoutExpired:
                _logger.warning("⚠️ TShark didn't stop gracefully; killing process.")
                self._process.kill()
        else:
            _logger.warning("No active capture process found to stop.")

    def export_to_csv(self, fields: list | None = None):
        """
        Converts the .pcapng file to a CSV based on specific fields.
        Example fields: ['frame.number', 'ip.src', 'ip.dst', 'http.request.uri']
        """
        if not fields:
            fields = ['frame.number', '_ws.col.Time', 'ip.src', 'ip.dst', 'protocol', '_ws.col.Info']

        csv_output = path.join(self.output_dir, "network_summary.csv")
        _logger.info(f"📄 Exporting specific fields to {csv_output}...")

        # -r: Read file
        # -T fields: Output format
        # -E header=y: Include CSV headers
        # -E separator=,: Use comma
        cmd = [self.tshark, "-r", self.pcap_file, "-T", "fields", "-E", "header=y", "-E", "separator=,"]
        
        for field in fields:
            cmd.extend(["-e", field])

        try:
            with open(csv_output, "w") as f:
                subprocess.run(cmd, stdout=f, check=True)
            _logger.info(f"✅ Export complete: {csv_output}")
            return csv_output
        except Exception as e:
            _logger.error(f"❌ Export failed: {e}")
            return None