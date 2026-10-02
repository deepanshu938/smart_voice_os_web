"""
AURA System Tools — Extended OS Automation
Covers: WhatsApp Call/Message, Volume, Screenshot, System Info,
        Timer, Weather, Web Search, Quick Notes, Power, Clipboard,
        Calculator, Spotify
"""

import os
import sys
import subprocess
import time
import threading
import urllib.parse
import urllib.request
import webbrowser
import json
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.append(str(Path(__file__).resolve().parent.parent))
from core.safety_guard import log_action


# ──────────────────────────────────────────────────────────────────────────────
# 📱  WHATSAPP CALL  (Fully Automated with pyautogui)
# ──────────────────────────────────────────────────────────────────────────────

def tool_whatsapp_call(contact_name: str, call_type: str = "voice") -> Dict[str, Any]:
    """
    Opens WhatsApp Desktop, searches for the contact, opens their chat,
    then CLICKS the voice or video call button automatically via pyautogui.
    """
    clean_name = contact_name.strip()
    try:
        # Step 1 — Launch WhatsApp Desktop
        os.system("start whatsapp:")
        time.sleep(4.0)  # Give WhatsApp time to fully load

        # Step 2 — Bring WhatsApp to foreground and search contact
        ps_search = f"""
        $wshell = New-Object -ComObject wscript.shell;
        $wshell.AppActivate('WhatsApp');
        Start-Sleep -Milliseconds 700;
        $wshell.SendKeys('^f');
        Start-Sleep -Milliseconds 600;
        $wshell.SendKeys('{clean_name}');
        Start-Sleep -Milliseconds 1000;
        $wshell.SendKeys('~');
        Start-Sleep -Milliseconds 1500;
        """
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_search],
            capture_output=True, timeout=15
        )
        time.sleep(1.8)

        # Step 3 — Click the call button with pyautogui
        try:
            import pyautogui
            import pygetwindow as gw
            pyautogui.FAILSAFE = False

            wa_windows = gw.getWindowsWithTitle("WhatsApp")
            if not wa_windows:
                raise RuntimeError("WhatsApp window not found")

            win = wa_windows[0]
            if win.isMinimized:
                win.restore()
            time.sleep(0.4)

            # WhatsApp Desktop button layout (from right edge of window):
            #   Video call button : ~60px from right,  ~45px from top
            #   Voice call button : ~100px from right, ~45px from top
            btn_y = win.top + 45
            btn_x = win.right - 60 if call_type == "video" else win.right - 100

            pyautogui.click(btn_x, btn_y)
            log_action("WHATSAPP_CALL", {"contact": clean_name, "type": call_type}, "SUCCESS")
            return {
                "status": "success",
                "message": (
                    f"{'📹 Video' if call_type == 'video' else '📞 Voice'} calling "
                    f"'{clean_name}' on WhatsApp!"
                )
            }

        except ImportError:
            log_action("WHATSAPP_CALL", {"contact": clean_name}, "PARTIAL")
            return {
                "status": "partial",
                "message": (
                    f"Opened WhatsApp and navigated to '{clean_name}'. "
                    "Please click the call button manually. "
                    "Install pyautogui for auto-click: pip install pyautogui pygetwindow"
                )
            }

    except Exception as e:
        return {"status": "error", "message": f"WhatsApp call failed: {str(e)}"}


# ──────────────────────────────────────────────────────────────────────────────
# 💬  WHATSAPP MESSAGE
# ──────────────────────────────────────────────────────────────────────────────

def tool_whatsapp_message(contact_name: str, message: str) -> Dict[str, Any]:
    """
    Opens WhatsApp Desktop, finds the contact, types the message and sends it
    automatically via Windows SendKeys automation.
    """
    clean_name = contact_name.strip()
    # Escape SendKeys special chars: { } + ^ % ~
    safe_msg = (message
                .replace("{", "{{")
                .replace("}", "}}")
                .replace("+", "{+}")
                .replace("^", "{^}")
                .replace("%", "{%}")
                .replace("~", "{~}"))
    try:
        os.system("start whatsapp:")
        time.sleep(3.5)

        ps_cmd = f"""
        $wshell = New-Object -ComObject wscript.shell;
        $wshell.AppActivate('WhatsApp');
        Start-Sleep -Milliseconds 700;
        $wshell.SendKeys('^f');
        Start-Sleep -Milliseconds 600;
        $wshell.SendKeys('{clean_name}');
        Start-Sleep -Milliseconds 1000;
        $wshell.SendKeys('~');
        Start-Sleep -Milliseconds 1300;
        $wshell.SendKeys('{safe_msg}');
        Start-Sleep -Milliseconds 500;
        $wshell.SendKeys('~');
        """
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, timeout=18
        )
        log_action("WHATSAPP_MESSAGE", {"contact": clean_name, "len": len(message)}, "SUCCESS")
        return {
            "status": "success",
            "message": f"✅ Message sent to '{clean_name}' on WhatsApp!"
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to send WhatsApp message: {str(e)}"}


# ──────────────────────────────────────────────────────────────────────────────
# 🔊  VOLUME CONTROL
# ──────────────────────────────────────────────────────────────────────────────

def tool_set_volume(action: str, level: Optional[int] = None) -> Dict[str, Any]:
    """
    Controls system volume.
    action: 'set' (requires level 0-100), 'up', 'down', 'mute', 'unmute'
    """
    action = action.lower().strip()
    try:
        # Primary: pycaw (precise Windows audio API)
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            vol_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
            current_scalar = vol_ctrl.GetMasterVolumeLevelScalar()

            if action == "mute":
                vol_ctrl.SetMute(1, None)
                return {"status": "success", "message": "🔇 Volume muted."}
            elif action == "unmute":
                vol_ctrl.SetMute(0, None)
                return {"status": "success", "message": "🔊 Volume unmuted."}
            elif action == "set" and level is not None:
                scalar = max(0.0, min(1.0, level / 100.0))
                vol_ctrl.SetMasterVolumeLevelScalar(scalar, None)
                vol_ctrl.SetMute(0, None)
                return {"status": "success", "message": f"🔊 Volume set to {level}%."}
            elif action in ("up", "increase"):
                new_scalar = min(1.0, current_scalar + 0.10)
                vol_ctrl.SetMasterVolumeLevelScalar(new_scalar, None)
                return {"status": "success", "message": f"🔊 Volume increased to {int(new_scalar*100)}%."}
            elif action in ("down", "decrease"):
                new_scalar = max(0.0, current_scalar - 0.10)
                vol_ctrl.SetMasterVolumeLevelScalar(new_scalar, None)
                return {"status": "success", "message": f"🔉 Volume decreased to {int(new_scalar*100)}%."}
        except ImportError:
            pass

        # Fallback: WScript.Shell virtual key codes (173=mute, 174=vol-down, 175=vol-up)
        vk_map = {
            "mute":     "[char]173",
            "unmute":   "[char]173",
            "up":       "[char]175",
            "increase": "[char]175",
            "down":     "[char]174",
            "decrease": "[char]174",
        }
        if action in vk_map:
            times = 5
            vk = vk_map[action]
            ps = f"$o=New-Object -ComObject WScript.Shell; for($i=0;$i -lt {times};$i++){{$o.SendKeys({vk})}}"
            subprocess.run(["powershell", "-c", ps], shell=True, timeout=5)
            return {"status": "success", "message": f"Volume {action}d. 🔊"}

        return {"status": "error", "message": f"Unknown action '{action}'. Use: set, up, down, mute, unmute"}

    except Exception as e:
        return {"status": "error", "message": f"Volume control failed: {str(e)}"}


# ──────────────────────────────────────────────────────────────────────────────
# 📸  SCREENSHOT
# ──────────────────────────────────────────────────────────────────────────────

def tool_take_screenshot(save_path: Optional[str] = None) -> Dict[str, Any]:
    """Takes a full-screen screenshot and saves it to Desktop (or custom path)."""
    try:
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
        except ImportError:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()

        if save_path:
            dest = Path(save_path)
        else:
            desktop = Path.home() / "Desktop"
            ts = time.strftime("%Y%m%d_%H%M%S")
            dest = desktop / f"Screenshot_{ts}.png"

        dest.parent.mkdir(parents=True, exist_ok=True)
        screenshot.save(str(dest))
        log_action("SCREENSHOT", {"path": str(dest)}, "SUCCESS")
        return {
            "status": "success",
            "path": str(dest),
            "message": f"📸 Screenshot saved: '{dest.name}' on Desktop."
        }
    except ImportError:
        return {"status": "error", "message": "Screenshot requires Pillow. Run: pip install Pillow pyautogui"}
    except Exception as e:
        return {"status": "error", "message": f"Screenshot failed: {str(e)}"}


# ──────────────────────────────────────────────────────────────────────────────
# 💻  SYSTEM INFO
# ──────────────────────────────────────────────────────────────────────────────

def tool_get_system_info(info_type: str = "all") -> Dict[str, Any]:
    """
    Returns live system stats.
    info_type: 'cpu', 'ram', 'battery', 'disk', 'all'
    """
    try:
        import psutil
        info: Dict[str, Any] = {}
        parts = []
        t = info_type.lower()

        if t in ("cpu", "all"):
            info["cpu_percent"] = psutil.cpu_percent(interval=1)
            info["cpu_cores"] = psutil.cpu_count(logical=True)
            parts.append(f"CPU: {info['cpu_percent']}% ({info['cpu_cores']} cores)")

        if t in ("ram", "memory", "all"):
            ram = psutil.virtual_memory()
            info["ram_total_gb"]  = round(ram.total / 1024**3, 1)
            info["ram_used_gb"]   = round(ram.used  / 1024**3, 1)
            info["ram_percent"]   = ram.percent
            parts.append(f"RAM: {info['ram_used_gb']}GB / {info['ram_total_gb']}GB ({ram.percent}%)")

        if t in ("battery", "all"):
            bat = psutil.sensors_battery()
            if bat:
                info["battery_percent"] = round(bat.percent, 1)
                info["battery_charging"] = bat.power_plugged
                status = "⚡ Charging" if bat.power_plugged else "🔋 Discharging"
                parts.append(f"Battery: {info['battery_percent']}% ({status})")

        if t in ("disk", "all"):
            disk = psutil.disk_usage("/")
            info["disk_total_gb"] = round(disk.total / 1024**3, 1)
            info["disk_free_gb"]  = round(disk.free  / 1024**3, 1)
            info["disk_percent"]  = disk.percent
            parts.append(f"Disk: {info['disk_free_gb']}GB free / {info['disk_total_gb']}GB total")

        summary = " | ".join(parts) if parts else "No data retrieved."
        return {"status": "success", "data": info, "message": summary}

    except ImportError:
        return {"status": "error", "message": "psutil not installed. Run: pip install psutil"}
    except Exception as e:
        return {"status": "error", "message": f"System info error: {str(e)}"}


# ──────────────────────────────────────────────────────────────────────────────
# ⏰  TIMER / ALARM
# ──────────────────────────────────────────────────────────────────────────────

_timers: Dict[str, threading.Thread] = {}

def tool_set_timer(seconds: int, label: str = "Timer") -> Dict[str, Any]:
    """Sets a countdown timer. Speaks aloud + shows notification when done."""
    if seconds <= 0:
        return {"status": "error", "message": "Please provide a positive number of seconds."}

    timer_id = f"timer_{int(time.time())}"

    def _fire(lbl: str, secs: int) -> None:
        time.sleep(secs)
        msg = f"⏰ {lbl} is done! Time's up!"
        print(f"\n\n[AURA ⏰]: {msg}\n")
        try:
            from voice.tts import TextToSpeechEngine
            TextToSpeechEngine().speak(msg)
        except Exception:
            pass
        # Windows toast notification
        try:
            ps_toast = (
                "Add-Type -AssemblyName System.Windows.Forms;"
                "[System.Windows.Forms.MessageBox]::Show("
                f"'AURA: {lbl} is complete!', 'AURA Timer', 0, 64)"
            )
            subprocess.run(["powershell", "-c", ps_toast], shell=True, timeout=30)
        except Exception:
            pass

    t = threading.Thread(target=_fire, args=(label, seconds), daemon=True)
    t.start()
    _timers[timer_id] = t

    mins, secs = divmod(seconds, 60)
    hrs,  mins = divmod(mins, 60)
    if hrs:
        time_str = f"{hrs}h {mins}m {secs}s"
    elif mins:
        time_str = f"{mins}m {secs}s"
    else:
        time_str = f"{secs}s"

    log_action("SET_TIMER", {"label": label, "seconds": seconds}, "SUCCESS")
    return {
        "status": "success",
        "timer_id": timer_id,
        "message": f"⏰ Timer set for {time_str}! I'll remind you when '{label}' is done."
    }


# ──────────────────────────────────────────────────────────────────────────────
# 🌤️  WEATHER  (wttr.in — no API key needed)
# ──────────────────────────────────────────────────────────────────────────────

def tool_get_weather(city: str = "") -> Dict[str, Any]:
    """Fetches current weather for any city using wttr.in (free, no API key)."""
    try:
        location = city.strip()
        url = f"https://wttr.in/{urllib.parse.quote(location)}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "AURA-Voice-OS/1.0"})
        raw  = urllib.request.urlopen(req, timeout=7).read().decode("utf-8")
        data = json.loads(raw)

        cur   = data["current_condition"][0]
        area  = data["nearest_area"][0]

        city_name   = area["areaName"][0]["value"]
        country     = area["country"][0]["value"]
        temp_c      = cur["temp_C"]
        feels_c     = cur["FeelsLikeC"]
        humidity    = cur["humidity"]
        description = cur["weatherDesc"][0]["value"]
        wind_kmph   = cur["windspeedKmph"]

        message = (
            f"🌤️ {city_name}, {country}: {description}, {temp_c}°C "
            f"(feels {feels_c}°C), Humidity {humidity}%, Wind {wind_kmph} km/h."
        )
        log_action("WEATHER", {"city": city_name}, "SUCCESS")
        return {
            "status": "success",
            "city": city_name,
            "temp_c": temp_c,
            "description": description,
            "message": message
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Couldn't fetch weather: {str(e)}. Check internet connection."
        }


# ──────────────────────────────────────────────────────────────────────────────
# 🔍  WEB SEARCH
# ──────────────────────────────────────────────────────────────────────────────

def tool_web_search(query: str) -> Dict[str, Any]:
    """Searches Google for the given query in the default browser."""
    try:
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        log_action("WEB_SEARCH", {"query": query}, "SUCCESS")
        return {"status": "success", "message": f"🔍 Searching Google for: '{query}'"}
    except Exception as e:
        return {"status": "error", "message": f"Web search failed: {str(e)}"}


# ──────────────────────────────────────────────────────────────────────────────
# 📝  QUICK NOTE
# ──────────────────────────────────────────────────────────────────────────────

def tool_quick_note(content: str, title: str = "") -> Dict[str, Any]:
    """Saves a spoken note to Desktop/AURA_Notes/ and opens it in Notepad."""
    try:
        notes_dir = Path.home() / "Desktop" / "AURA_Notes"
        notes_dir.mkdir(exist_ok=True)

        ts = time.strftime("%Y-%m-%d_%H-%M-%S")
        safe_title = "".join(c for c in title if c.isalnum() or c in " _-").strip()
        filename = f"{safe_title}_{ts}.txt" if safe_title else f"Note_{ts}.txt"
        note_path = notes_dir / filename

        note_content = f"[AURA Note — {time.strftime('%d %b %Y, %I:%M %p')}]\n\n{content}\n"
        note_path.write_text(note_content, encoding="utf-8")
        os.startfile(str(note_path))

        log_action("QUICK_NOTE", {"file": str(note_path)}, "SUCCESS")
        return {
            "status": "success",
            "path": str(note_path),
            "message": f"📝 Note saved as '{filename}' in Desktop → AURA_Notes."
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to save note: {str(e)}"}


# ──────────────────────────────────────────────────────────────────────────────
# ⚡  POWER ACTIONS
# ──────────────────────────────────────────────────────────────────────────────

def tool_power_action(action: str, delay_seconds: int = 30) -> Dict[str, Any]:
    """
    Performs system power actions.
    action: 'lock', 'sleep', 'shutdown', 'restart', 'cancel'
    delay_seconds: seconds before shutdown/restart (default 30)
    """
    action = action.lower().strip()
    try:
        if action == "lock":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            return {"status": "success", "message": "🔒 PC locked."}

        elif action == "sleep":
            subprocess.run([
                "powershell", "-c",
                "Add-Type -Assembly System.Windows.Forms; "
                "[System.Windows.Forms.Application]::SetSuspendState('Suspend',$false,$false)"
            ], shell=True)
            return {"status": "success", "message": "💤 PC going to sleep..."}

        elif action == "shutdown":
            t = max(0, delay_seconds)
            subprocess.run(["shutdown", "/s", "/t", str(t)], shell=True)
            return {"status": "success", "message": f"🛑 PC will shut down in {t}s. Goodbye!"}

        elif action == "restart":
            t = max(0, delay_seconds)
            subprocess.run(["shutdown", "/r", "/t", str(t)], shell=True)
            return {"status": "success", "message": f"🔄 PC will restart in {t}s."}

        elif action in ("cancel", "cancel_shutdown"):
            subprocess.run(["shutdown", "/a"], shell=True)
            return {"status": "success", "message": "✅ Shutdown/restart cancelled."}

        return {
            "status": "error",
            "message": f"Unknown action '{action}'. Use: lock, sleep, shutdown, restart, cancel"
        }
    except Exception as e:
        return {"status": "error", "message": f"Power action failed: {str(e)}"}


# ──────────────────────────────────────────────────────────────────────────────
# 📋  CLIPBOARD
# ──────────────────────────────────────────────────────────────────────────────

def tool_clipboard_action(action: str, text: str = "") -> Dict[str, Any]:
    """
    Manages clipboard.
    action: 'copy' (text required), 'read', 'paste'
    """
    try:
        if action == "copy":
            if not text:
                return {"status": "error", "message": "No text provided to copy."}
            safe = text.replace("'", '"')
            subprocess.run(
                ["powershell", "-c", f"Set-Clipboard -Value '{safe}'"],
                shell=True, timeout=5
            )
            preview = text[:60] + "..." if len(text) > 60 else text
            return {"status": "success", "message": f"📋 Copied: '{preview}'"}

        elif action == "read":
            res = subprocess.run(
                ["powershell", "-c", "Get-Clipboard"],
                capture_output=True, text=True, shell=True, timeout=5
            )
            content = res.stdout.strip()
            if not content:
                return {"status": "success", "message": "Clipboard is empty."}
            return {
                "status": "success",
                "content": content,
                "message": f"📋 Clipboard: '{content[:200]}'"
            }

        elif action == "paste":
            try:
                import pyautogui
                pyautogui.hotkey("ctrl", "v")
                return {"status": "success", "message": "📋 Pasted clipboard content."}
            except ImportError:
                return {"status": "error", "message": "pip install pyautogui for paste support."}

        return {"status": "error", "message": f"Unknown action '{action}'. Use: copy, read, paste"}
    except Exception as e:
        return {"status": "error", "message": f"Clipboard action failed: {str(e)}"}


# ──────────────────────────────────────────────────────────────────────────────
# 🧮  CALCULATOR
# ──────────────────────────────────────────────────────────────────────────────

def tool_calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluates a math expression (no eval() abuse).
    Supports: +, -, *, /, **, % and spoken forms like 'plus', 'times', etc.
    """
    import ast, operator

    _OPS = {
        ast.Add:  operator.add,
        ast.Sub:  operator.sub,
        ast.Mult: operator.mul,
        ast.Div:  operator.truediv,
        ast.Pow:  operator.pow,
        ast.Mod:  operator.mod,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            return _OPS[type(node.op)](_eval(node.operand))
        raise ValueError(f"Unsupported node: {type(node).__name__}")

    try:
        expr = (expression.strip()
                .replace("×", "*").replace("÷", "/").replace("^", "**")
                .replace("plus", "+").replace("minus", "-")
                .replace("times", "*").replace("multiplied by", "*")
                .replace("divided by", "/").replace("mod", "%"))

        tree   = ast.parse(expr, mode="eval")
        result = _eval(tree.body)
        result = int(result) if isinstance(result, float) and result.is_integer() else round(result, 6)

        log_action("CALCULATE", {"expr": expression, "result": result}, "SUCCESS")
        return {
            "status": "success",
            "result": result,
            "message": f"🧮 {expression} = {result}"
        }
    except ZeroDivisionError:
        return {"status": "error", "message": "❌ Cannot divide by zero!"}
    except Exception as e:
        return {"status": "error", "message": f"Could not calculate '{expression}': {str(e)}"}


# ──────────────────────────────────────────────────────────────────────────────
# 🎵  SPOTIFY
# ──────────────────────────────────────────────────────────────────────────────

def tool_play_on_spotify(query: str) -> Dict[str, Any]:
    """Searches and plays a song/artist on Spotify Desktop via URI scheme."""
    try:
        clean = query.strip()
        uri   = f"spotify:search:{urllib.parse.quote(clean)}"
        os.system(f"start {uri}")
        log_action("PLAY_SPOTIFY", {"query": clean}, "SUCCESS")
        return {"status": "success", "message": f"🎵 Searching Spotify for: '{clean}'"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to open Spotify: {str(e)}"}
