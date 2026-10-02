import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import CORE_SEARCH_DIRS, EXT_MAP, DESKTOP_DIR, DOWNLOADS_DIR, DOCUMENTS_DIR
from core.file_resolver import scan_file_system, extract_content_snippet
from core.safety_guard import safe_delete_file, log_action

def tool_find_files(
    query: str,
    file_type: Optional[str] = None,
    date_range: Optional[str] = None,
    content_hint: Optional[str] = None
) -> Dict[str, Any]:
    """Searches for files across user folders using multi-tier fuzzy and content matching."""
    results = scan_file_system(
        query=query,
        file_type=file_type,
        date_range=date_range,
        content_hint=content_hint,
        max_results=5
    )
    if not results:
        return {
            "status": "not_found",
            "message": f"No matching files found for '{query}'. Try giving an extra hint like recent date, extension, or a word inside the file.",
            "candidates": []
        }
    return {
        "status": "found",
        "count": len(results),
        "candidates": results
    }

import webbrowser
import urllib.parse
import urllib.request
import re

def tool_play_on_youtube(query: str) -> Dict[str, Any]:
    """Finds the top matching video on YouTube and starts playing it directly with autoplay."""
    clean_query = query.replace("play", "").replace("youtube", "").replace("song", "").strip() or query
    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(clean_query)}"
    
    play_url = search_url
    try:
        # Scrape the first video ID so the video starts playing immediately
        req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        html = urllib.request.urlopen(req, timeout=4).read().decode("utf-8")
        video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)
        if video_ids:
            # Direct video link with autoplay
            play_url = f"https://www.youtube.com/watch?v={video_ids[0]}&autoplay=1"
    except Exception:
        play_url = search_url

    try:
        webbrowser.open(play_url)
        log_action("PLAY_YOUTUBE", {"query": query, "url": play_url}, "SUCCESS")
        return {"status": "success", "message": f"Playing '{clean_query}' directly on YouTube with autoplay."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to play YouTube video: {str(e)}"}

def tool_whatsapp_call(contact_name: str) -> Dict[str, Any]:
    """Opens WhatsApp Desktop, searches for the contact, and opens chat to place the call."""
    clean_name = contact_name.strip()
    try:
        # Launch native WhatsApp Desktop app
        os.system("start whatsapp:")
        log_action("WHATSAPP_CALL", {"contact": clean_name}, "SUCCESS")

        # Automate search using Windows native WScript.Shell SendKeys
        ps_cmd = f"""
        $wshell = New-Object -ComObject wscript.shell;
        Start-Sleep -Seconds 2;
        $wshell.AppActivate('WhatsApp');
        Start-Sleep -Milliseconds 400;
        $wshell.SendKeys('^f');
        Start-Sleep -Milliseconds 400;
        $wshell.SendKeys('{clean_name}');
        Start-Sleep -Milliseconds 600;
        $wshell.SendKeys('~');
        """
        subprocess.Popen(["powershell", "-NoProfile", "-Command", ps_cmd], shell=True)
        return {
            "status": "success",
            "message": f"Opened WhatsApp Desktop, searched for '{clean_name}', and opened their chat window so you can start talking."
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to automate WhatsApp call: {str(e)}"}

def tool_open_website(url: str) -> Dict[str, Any]:
    """Opens a website URL in the user's default browser."""
    target_url = url.strip()
    if not target_url.startswith(("http://", "https://")):
        target_url = f"https://{target_url}"
    try:
        webbrowser.open(target_url)
        log_action("OPEN_WEBSITE", {"url": target_url}, "SUCCESS")
        return {"status": "success", "message": f"Opened website: {target_url}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to open website: {str(e)}"}

def tool_open_file_or_app(target: str) -> Dict[str, Any]:
    """Opens a file, launches a Windows application, or opens a website."""
    # Check if target is a web or YouTube request
    target_lower = target.lower().strip()
    if "youtube" in target_lower or "play" in target_lower:
        return tool_play_on_youtube(target)
    if target_lower.startswith(("http://", "https://", "www.")) or target_lower.endswith((".com", ".org", ".net", ".in")):
        return tool_open_website(target)

    path = Path(target)
    if path.exists():
        try:
            os.startfile(str(path))
            log_action("OPEN_FILE", {"target": str(path)}, "SUCCESS")
            return {"status": "success", "message": f"Opened file: {path.name}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to open file: {str(e)}"}
    
    # Check for Windows Modern/Store App protocols (WhatsApp, Spotify, Telegram, etc.)
    app_protocols = {
        "whatsapp": "whatsapp:",
        "spotify": "spotify:",
        "telegram": "tg:",
        "discord": "discord:",
        "slack": "slack:",
        "settings": "ms-settings:",
        "camera": "microsoft.windows.camera:",
        "mail": "mailto:",
        "store": "ms-windows-store:",
        "photos": "ms-photos:"
    }
    
    for app_name, proto in app_protocols.items():
        if app_name in target_lower:
            try:
                os.system(f"start {proto}")
                log_action("LAUNCH_APP_PROTOCOL", {"app": app_name, "protocol": proto}, "SUCCESS")
                return {"status": "success", "message": f"Opened {app_name.capitalize()} desktop application."}
            except Exception as e:
                return {"status": "error", "message": f"Could not launch {app_name}: {str(e)}"}

    # Try launching known app names
    known_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "terminal": "wt.exe",
        "chrome": "chrome.exe",
        "browser": "msedge.exe",
        "edge": "msedge.exe",
        "paint": "mspaint.exe",
        "taskmgr": "taskmgr.exe"
    }
    
    for name, exe in known_apps.items():
        if name in target_lower:
            try:
                subprocess.Popen([exe], shell=True)
                log_action("LAUNCH_APP", {"app": exe}, "SUCCESS")
                return {"status": "success", "message": f"Launched application: {name}"}
            except Exception as e:
                return {"status": "error", "message": f"Could not launch {name}: {str(e)}"}
                
    return {"status": "error", "message": f"Target not found as file or known application: {target}"}

def tool_read_file_snippet(file_path_str: str) -> Dict[str, Any]:
    """Reads the text inside a file so the LLM can answer questions about it."""
    path = Path(file_path_str)
    if not path.exists():
        return {"status": "error", "message": f"File does not exist: {file_path_str}"}
        
    snippet = extract_content_snippet(path, max_chars=8000)
    if not snippet.strip():
        return {"status": "empty", "message": f"File '{path.name}' is empty or content could not be extracted as text."}
        
    return {
        "status": "success",
        "filename": path.name,
        "content_length": len(snippet),
        "content": snippet
    }

def tool_organize_folder(folder_name: str = "Desktop", dry_run: bool = True) -> Dict[str, Any]:
    """Organizes files in Desktop or Downloads by file type into dedicated subfolders."""
    folder_map = {
        "desktop": DESKTOP_DIR,
        "downloads": DOWNLOADS_DIR,
        "documents": DOCUMENTS_DIR
    }
    target_dir = folder_map.get(folder_name.lower().strip(), Path(folder_name))
    if not target_dir.exists():
        return {"status": "error", "message": f"Directory not found: {target_dir}"}
        
    plan = []
    # Identify loose files (do not move existing subfolders or shortcuts)
    for item in target_dir.iterdir():
        if item.is_file() and not item.name.startswith(".") and item.suffix.lower() != ".lnk":
            ext = item.suffix.lower()
            category = "Other"
            for cat, exts in EXT_MAP.items():
                if ext in exts:
                    category = cat.capitalize() + "s"
                    break
            
            dest_dir = target_dir / category
            plan.append({
                "file": item.name,
                "current_path": str(item),
                "target_folder": category,
                "target_path": str(dest_dir / item.name)
            })
            
    if dry_run:
        return {
            "status": "dry_run_preview",
            "folder": str(target_dir),
            "files_to_move_count": len(plan),
            "plan_summary": f"Found {len(plan)} files to organize into categories. Call with dry_run=False to execute.",
            "preview": plan[:10]
        }
        
    # Execute organization
    moved_count = 0
    for move_info in plan:
        dest_folder = Path(move_info["target_path"]).parent
        dest_folder.mkdir(exist_ok=True)
        try:
            shutil.move(move_info["current_path"], move_info["target_path"])
            moved_count += 1
        except Exception:
            pass
            
    log_action("ORGANIZE_FOLDER", {"folder": str(target_dir), "moved_count": moved_count}, "SUCCESS")
    return {
        "status": "success",
        "message": f"Successfully organized {moved_count} files in {target_dir.name}."
    }

def tool_safe_delete(file_path: str, confirmed: bool = False) -> Dict[str, Any]:
    """Deletes a file safely via Windows Recycle Bin with mandatory user confirmation."""
    success, msg = safe_delete_file(file_path, confirmed=confirmed)
    return {
        "status": "success" if success else "pending_or_failed",
        "requires_confirmation": not confirmed and not success,
        "message": msg
    }
