from os import path, remove
import subprocess
import time

class ProcmonController:
    def __init__(self, procmon_path: str, output_path: str, log_name="log"):
        self.procmon = path.abspath(procmon_path)
        self.pml_file = path.abspath(path.join(output_path, f"{log_name}.PML"))
        self.csv_file = path.abspath(path.join(output_path, f"{log_name}.CSV"))

    def capture(self, duration_sec: int, convert_to_csv: bool = True, cleanup: bool = False):
        """
        Executes a full capture cycle.
        Params:
            convert_to_csv: If True, converts the .PML file to the CSV format.
            cleanup: If True, deletes the .PML file after successful CSV conversion.
        """
        self.start_capture()
        
        print(f"Recording for {duration_sec} seconds...")
        time.sleep(duration_sec)
        
        self.stop_capture()
        if convert_to_csv:
            success = self.convert_to_csv()
            if success and cleanup:
                self.cleanup_pml()

    def start_capture(self):
        print("🚀 Starting Procmon capture...")
        # /BackingFile: Where to save the binary log
        # /Quiet: No configuration dialogs
        # /Minimized: Keep it out of the way
        # /AcceptEula ensures no hidden popups block the process
        subprocess.Popen([self.procmon, "/AcceptEula", "/BackingFile", self.pml_file, "/Quiet", "/Minimized"])

    def stop_capture(self):
        print("🛑 Stopping Procmon...")
        # /Terminate: Signals the running instance to stop and exit
        subprocess.run([self.procmon, "/Terminate"], check=True)
        
        # CRITICAL: Wait until the .pml file is actually written and released
        print("⏳ Waiting for file handle release...")
        timeout = 10
        while timeout > 0:
            if path.exists(self.pml_file) and path.getsize(self.pml_file) > 0:
                time.sleep(2) # Extra padding for disk flush
                break
            time.sleep(1)
            timeout -= 1
            
        print(f"✅ Log saved to {self.pml_file}")

    def convert_to_csv(self) -> bool:
        if not path.exists(self.pml_file):
            print(f"❌ Error: {self.pml_file} was never created.")
            return False
        
        print(f"📄 Converting {self.pml_file} to CSV...")
        # Procmon commands
        # /OpenLog: Open log 
        # /SaveAs: Path to output CSV
        subprocess.run([self.procmon, "/OpenLog", self.pml_file, "/SaveAs", self.csv_file, "/Quiet"], 
                       check=True, capture_output=True, text=True)
        if path.exists(self.csv_file):
            print(f"✅ Success! Log saved to: {self.csv_file}")
            return True
        else:
            print("❌ Conversion failed.")
            return False
        
    def cleanup_pml(self):
        """Deletes the large binary .PML file to save disk space."""
        if path.exists(self.pml_file):
            try:
                remove(self.pml_file)
                print(f"🧹 Cleaned up binary file: {self.pml_file}")
            except OSError as e:
                print(f"⚠️ Could not delete {self.pml_file}: {e}")