import ctypes
import sys

def run_as_admin():
    """Checks if the script is admin. If not, relaunches with admin rights."""
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if not is_admin:
        print("Privileges insufficient. Relaunching as Administrator...")
        # Re-run the script with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()