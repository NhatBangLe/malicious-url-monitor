from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ScriptArguments:
    script_path: str
    target_url: str
    signal_file: str = "AUDIT_COMPLETED"
    duration: int = 30
    output_path: str = "Z:\\"
    regview_path: Optional[str] = None
    procmon_path: Optional[str] = None
    tshark_path: Optional[str] = None
    tshark_fields: Optional[List[str]] = None
    interface_num: int = 1
