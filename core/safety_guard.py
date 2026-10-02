import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

try:
    from send2trash import send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False

LOG_FILE = Path.home() / ".smart_voice_os_audit.json"

class SafetyLevel:
    SAFE = "SAFE"            # e.g., read, search, open
    MODERATE = "MODERATE"    # e.g., rename, move
    CRITICAL = "CRITICAL"    # e.g., delete, clear folder


def log_action(action_type: str, details: Dict[str, Any], status: str):
    """Logs every action to a persistent JSON audit trail."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action_type,
        "details": details,
        "status": status
    }
    try:
        logs = []
        if LOG_FILE.exists():
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        logs.append(entry)
        # Keep last 500 actions
        logs = logs[-500:]
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
    except Exception:
        pass


def safe_delete_file(file_path_str: str, confirmed: bool = False) -> Tuple[bool, str]:
    """
    Safely deletes a file by sending it to the Windows Recycle Bin.
    Requires explicit confirmation to prevent accidental loss.
    """
    path = Path(file_path_str)
    if not path.exists():
        return False, f"File does not exist: {file_path_str}"

    if not confirmed:
        return False, f"Confirmation Required: Are you sure you want to delete '{path.name}'? Please say 'yes' or confirm."

    try:
        if HAS_SEND2TRASH:
            send2trash(str(path))
            log_action("DELETE_RECYCLE_BIN", {"file": str(path)}, "SUCCESS")
            return True, f"'{path.name}' has been moved safely to the Recycle Bin."
        else:
            # Fallback if send2trash is not installed: move to a backup quarantine folder
            quarantine = Path.home() / ".smart_voice_quarantine"
            quarantine.mkdir(exist_ok=True)
            target = quarantine / f"{int(datetime.now().timestamp())}_{path.name}"
            path.rename(target)
            log_action("MOVE_QUARANTINE", {"source": str(path), "target": str(target)}, "SUCCESS")
            return True, f"'{path.name}' moved safely to quarantine folder at {quarantine}."
    except Exception as e:
        log_action("DELETE_FAILED", {"file": str(path), "error": str(e)}, "FAILED")
        return False, f"Error deleting file: {str(e)}"
