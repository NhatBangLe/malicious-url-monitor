import time
from controllers.procmon import ProcmonController
from helpers import run_as_admin


if __name__ == "__main__":
    curr_time = time.gmtime()
    log_name = f'log_{str(curr_time.tm_year)}-{str(curr_time.tm_mon)}-{str(curr_time.tm_mday)}_{str(curr_time.tm_hour)}-{str(curr_time.tm_min)}-{str(curr_time.tm_sec)}'
    pm = ProcmonController(procmon_path="C:\\Users\\Admin\\Desktop\\Projects\\security\\ProcessMonitor\\Procmon.exe", 
                           output_path="C:\\Users\\Admin\\Desktop\\Projects\\security\\logs",
                           log_name=log_name)
    
    run_as_admin()
    pm.capture(duration_sec=10, convert_to_csv=True)