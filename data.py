from dataclasses import dataclass


@dataclass
class ScriptArguments:
    target_url: str
    signal_file: str = "AUDIT_COMPLETED"
    duration: int = 30
    output_path: str = "Z:\\"
    regview_path: str | None = None
    procmon_path: str | None = None
    tshark_path: str | None = None
    tshark_fields: list[str] | None = None
    interface_num: int = 1
