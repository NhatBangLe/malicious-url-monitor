import logging
import time
from controllers.procmon import ProcmonController
from controllers.registry import RegistryController
from helpers import run_as_admin


# Configure logging to show time, level, and message
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    curr_time = time.gmtime()
    time_str = f'{str(curr_time.tm_year)}-{str(curr_time.tm_mon)}-{str(curr_time.tm_mday)}_{str(curr_time.tm_hour)}-{str(curr_time.tm_min)}-{str(curr_time.tm_sec)}'
    run_as_admin()
    
    # pm = ProcmonController(procmon_path="C:\\Users\\Admin\\Desktop\\Projects\\security\\ProcessMonitor\\Procmon.exe", 
    #                        output_path="C:\\Users\\Admin\\Desktop\\Projects\\security\\logs",
    #                        log_name=f'log_{time_str}')
    # pm.capture(duration_sec=10, convert_to_csv=True)
    
    monitor = RegistryController("C:\\Users\\Admin\\Desktop\\Projects\\security\\registrychangesview-x64\\RegistryChangesView.exe")
    # 1. Take initial state
    monitor.capture_changes(duration_sec=10, 
                            output_name=f'regdiff_{time_str}',
                            output_dir_path="C:\\Users\\Admin\\Desktop\\Projects\\security\\reg")