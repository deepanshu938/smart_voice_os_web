"""
AURA LLM Client — Tool Schema, Dispatcher & System Prompt
All tools wired up: file ops, WhatsApp, YouTube, volume, screenshot,
system info, timer, weather, search, notes, power, clipboard, calc, Spotify,
email, calendar, file ops, brightness, Wi-Fi, documents, news, briefing, smart home.
"""

import json
from typing import Dict, Any
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import GROQ_API_KEY, GROQ_MODEL, GEMINI_API_KEY, GEMINI_MODEL, LLM_PROVIDER

# ── Core OS tools (file search, open, organize, delete, YouTube, website) ────
from core.os_tools import (
    tool_find_files,
    tool_open_file_or_app,
    tool_read_file_snippet,
    tool_organize_folder,
    tool_safe_delete,
    tool_play_on_youtube,
    tool_open_website,
)

# ── System & automation tools ─────────────────────────────────────────────────
from core.system_tools import (
    tool_whatsapp_call,
    tool_whatsapp_message,
    tool_set_volume,
    tool_take_screenshot,
    tool_get_system_info,
    tool_set_timer,
    tool_get_weather,
    tool_web_search,
    tool_quick_note,
    tool_power_action,
    tool_clipboard_action,
    tool_calculate,
    tool_play_on_spotify,
)

# ── Advanced tools (Email, Calendar, File Ops, Brightness, Wi-Fi, Docs, News, Smart Home) ──
from core.advanced_tools import (
    tool_send_email,
    tool_read_emails,
    tool_create_calendar_event,
    tool_file_operation,
    tool_open_multiple_apps,
    tool_set_brightness,
    tool_wifi_control,
    tool_create_document,
    tool_get_news,
    tool_morning_briefing,
    tool_smart_home,
)


# ─────────────────────────────────────────────────────────────────────────────
#  TOOLS SCHEMA  (OpenAI / Groq compatible JSON Schema)
# ─────────────────────────────────────────────────────────────────────────────

TOOLS_SCHEMA = [

    # ── File Management ───────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "find_files",
            "description": "Searches for user files when the exact path is unknown. Uses fuzzy name matching, modification date, and in-file text inspection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query":        {"type": "string", "description": "Keyword, topic, or file name hint (e.g. 'electricity bill', 'resume', 'machine learning')"},
                    "file_type":    {"type": "string", "enum": ["document", "image", "archive", "code", "media"], "description": "Optional file category"},
                    "date_range":   {"type": "string", "description": "Recency filter: 'today', 'yesterday', 'this week', 'last week', 'last month'"},
                    "content_hint": {"type": "string", "description": "A word or phrase expected inside the file content"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_file_or_app",
            "description": "Opens a file in its default program, launches a Windows app (e.g. notepad, calc, chrome, whatsapp, spotify), or opens a website.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Full file path, app name, or URL to open"}
                },
                "required": ["target"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_snippet",
            "description": "Reads text inside a file so you can summarize it or answer questions about its content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path_str": {"type": "string", "description": "Exact file path to read"}
                },
                "required": ["file_path_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "organize_folder",
            "description": "Cleans up cluttered folders by grouping loose files into categorized subfolders (Images, Documents, Videos, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder_name": {"type": "string", "description": "Folder to organize: 'Desktop', 'Downloads', or 'Documents'"},
                    "dry_run":     {"type": "boolean", "description": "True to preview changes, False to actually move files"}
                },
                "required": ["folder_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "safe_delete",
            "description": "Deletes a file to the Windows Recycle Bin. Requires explicit user confirmation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path of the file to delete"},
                    "confirmed": {"type": "boolean", "description": "Set True only if user explicitly said yes/confirmed"}
                },
                "required": ["file_path"]
            }
        }
    },

    # ── Media ─────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "play_on_youtube",
            "description": "Searches and plays a song, video, or music on YouTube in the browser with autoplay.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Song name, video title, or artist (e.g. 'saki saki', 'arijit singh')"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_on_spotify",
            "description": "Searches and plays music on the Spotify Desktop app.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Song name, artist, album, or playlist to search on Spotify"}
                },
                "required": ["query"]
            }
        }
    },

    # ── Browser / Web ─────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "open_website",
            "description": "Opens any website in the default browser.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Website URL or domain (e.g. 'google.com', 'github.com')"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches Google for any query and opens results in the browser. Use for general knowledge, news, how-to questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query to look up on Google"}
                },
                "required": ["query"]
            }
        }
    },

    # ── WhatsApp ──────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "whatsapp_call",
            "description": "Opens WhatsApp Desktop, finds the contact, and AUTOMATICALLY clicks the voice or video call button. Use when user says 'call [name]', 'WhatsApp call [name]', 'video call [name]'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {"type": "string", "description": "Name of the WhatsApp contact to call (e.g. 'Maa', 'Papa', 'Rohan')"},
                    "call_type":    {"type": "string", "enum": ["voice", "video"], "description": "Type of call: 'voice' (default) or 'video'"}
                },
                "required": ["contact_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "whatsapp_message",
            "description": "Opens WhatsApp Desktop and AUTOMATICALLY sends a text message to the specified contact.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {"type": "string", "description": "WhatsApp contact name to send the message to"},
                    "message":      {"type": "string", "description": "The message text to send"}
                },
                "required": ["contact_name", "message"]
            }
        }
    },

    # ── Volume ────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Controls system audio volume. Can set exact level, increase, decrease, mute, or unmute.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["set", "up", "down", "mute", "unmute", "increase", "decrease"], "description": "Volume action to perform"},
                    "level":  {"type": "integer", "description": "Volume level 0-100 (only needed when action='set')"}
                },
                "required": ["action"]
            }
        }
    },

    # ── Screenshot ────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Takes a full-screen screenshot and saves it to Desktop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "save_path": {"type": "string", "description": "Optional custom file path to save the screenshot (default: Desktop)"}
                },
                "required": []
            }
        }
    },

    # ── System Info ───────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Returns live PC stats: CPU usage, RAM, battery percentage, and disk space.",
            "parameters": {
                "type": "object",
                "properties": {
                    "info_type": {"type": "string", "enum": ["cpu", "ram", "battery", "disk", "all"], "description": "Which stat to fetch (default: 'all')"}
                },
                "required": []
            }
        }
    },

    # ── Timer ─────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "set_timer",
            "description": "Sets a countdown timer. Speaks aloud and shows a popup when done. Convert minutes/hours to seconds before calling.",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {"type": "integer", "description": "Duration in seconds (e.g. 5 minutes = 300, 1 hour = 3600)"},
                    "label":   {"type": "string", "description": "Label or reason for the timer (e.g. 'Tea', 'Workout', 'Meeting')"}
                },
                "required": ["seconds"]
            }
        }
    },

    # ── Weather ───────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Gets current weather info (temperature, humidity, wind, conditions) for any city. Free, no API key needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name (e.g. 'Delhi', 'Mumbai', 'London'). Leave empty for current location."}
                },
                "required": []
            }
        }
    },

    # ── Quick Note ────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "quick_note",
            "description": "Saves a voice/text note to Desktop → AURA_Notes folder and opens it in Notepad.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The note text to save"},
                    "title":   {"type": "string", "description": "Optional title/filename for the note"}
                },
                "required": ["content"]
            }
        }
    },

    # ── Power ─────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "power_action",
            "description": "Performs system power actions: lock screen, sleep, shutdown, restart, or cancel a pending shutdown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action":         {"type": "string", "enum": ["lock", "sleep", "shutdown", "restart", "cancel"], "description": "Power action to perform"},
                    "delay_seconds":  {"type": "integer", "description": "Seconds delay before shutdown/restart (default: 30)"}
                },
                "required": ["action"]
            }
        }
    },

    # ── Clipboard ─────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "clipboard_action",
            "description": "Manages the Windows clipboard: copy text to clipboard, read what's currently in clipboard, or paste clipboard content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["copy", "read", "paste"], "description": "Clipboard action"},
                    "text":   {"type": "string", "description": "Text to copy (only needed when action='copy')"}
                },
                "required": ["action"]
            }
        }
    },

    # ── Calculator ────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluates math expressions instantly. Handles +, -, *, /, **, % and spoken forms like 'plus', 'times', 'divided by'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression to evaluate (e.g. '25 * 4', '2 ** 10', '355 / 113')"}
                },
                "required": ["expression"]
            }
        }
    },

    # ── Email ─────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Sends an email via Gmail. Requires GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env. Use for 'email bhejo', 'mail karo', 'send mail to [name]'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to":      {"type": "string", "description": "Recipient email address (e.g. 'someone@gmail.com')"},
                    "subject": {"type": "string", "description": "Email subject line"},
                    "body":    {"type": "string", "description": "Email body text"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_emails",
            "description": "Reads and summarizes the latest emails from Gmail inbox. Use for 'emails dekho', 'mail check karo', 'koi naya mail hai kya'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "count":       {"type": "integer", "description": "Number of emails to fetch (default: 5)"},
                    "unread_only": {"type": "boolean", "description": "True for unread only (default), False for all recent"}
                },
                "required": []
            }
        }
    },

    # ── Calendar ──────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Creates a meeting or reminder in Windows Calendar/Outlook. Use for 'meeting set karo', 'reminder lagao', 'schedule a call'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title":             {"type": "string",  "description": "Event/meeting title"},
                    "date_str":          {"type": "string",  "description": "Date: 'today', 'tomorrow', 'Monday', or 'YYYY-MM-DD'"},
                    "time_str":          {"type": "string",  "description": "Time in 24h format 'HH:MM' (e.g. '14:30' for 2:30 PM)"},
                    "duration_minutes":  {"type": "integer", "description": "Duration in minutes (default: 60)"},
                    "description":       {"type": "string",  "description": "Optional event description/notes"},
                    "location":          {"type": "string",  "description": "Optional location"}
                },
                "required": ["title", "date_str"]
            }
        }
    },

    # ── File Operations ───────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "file_operation",
            "description": "Copies, moves, or renames a file. First use find_files to get the exact path, then call this. Use for 'copy karo', 'move karo', 'rename karo'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action":       {"type": "string", "enum": ["copy", "move", "rename"], "description": "Operation to perform"},
                    "source_path":  {"type": "string", "description": "Full path of the source file"},
                    "destination":  {"type": "string", "description": "Destination folder path (for copy/move)"},
                    "new_name":     {"type": "string", "description": "New filename with extension (for rename, e.g. 'report_final.pdf')"}
                },
                "required": ["action", "source_path"]
            }
        }
    },

    # ── Multi-App Launch ──────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "open_multiple_apps",
            "description": "Opens multiple applications at once simultaneously. Use for 'chrome aur spotify dono kholo', 'open WhatsApp and YouTube together'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_list": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of app names to open (e.g. ['chrome', 'spotify', 'whatsapp'])"
                    }
                },
                "required": ["app_list"]
            }
        }
    },

    # ── Brightness ────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "set_brightness",
            "description": "Controls screen brightness. Use for 'brightness badhao', 'screen dim karo', 'brightness 50 karo'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["set", "up", "down", "get", "increase", "decrease"], "description": "Brightness action"},
                    "level":  {"type": "integer", "description": "Brightness level 0-100 (only for action='set')"}
                },
                "required": ["action"]
            }
        }
    },

    # ── Wi-Fi ─────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "wifi_control",
            "description": "Controls Wi-Fi: check status, list networks, connect, disconnect. Use for 'WiFi status', 'kaun sa network connected hai', 'WiFi connect karo'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["status", "list", "connect", "disconnect", "enable", "disable"], "description": "Wi-Fi action"},
                    "ssid":   {"type": "string", "description": "Network name to connect to (only for action='connect')"}
                },
                "required": ["action"]
            }
        }
    },

    # ── Documents ─────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "create_document",
            "description": "Creates a Word (.docx) or Excel (.xlsx) document with optional content, then opens it. Use for 'Word file banao', 'Excel sheet banao', 'ek document create karo'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_type": {"type": "string", "enum": ["word", "excel"], "description": "Document type: 'word' for .docx, 'excel' for .xlsx"},
                    "filename": {"type": "string", "description": "File name without extension"},
                    "content":  {"type": "string", "description": "Optional: text content for Word, or CSV-style rows for Excel (e.g. 'Name,Age\\nAli,25')"},
                    "folder":   {"type": "string", "description": "Save location: 'Desktop', 'Documents', or 'Downloads' (default: Documents)"}
                },
                "required": ["doc_type", "filename"]
            }
        }
    },

    # ── News ──────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Fetches latest news headlines via Google News RSS. Free, no API key. Use for 'news sunao', 'aaj ki khabar', 'technology news', 'sports news'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "News topic: empty for top stories, or 'technology', 'sports', 'business', 'india', 'cricket', etc."},
                    "count": {"type": "integer", "description": "Number of headlines (default: 5, max: 10)"}
                },
                "required": []
            }
        }
    },

    # ── Morning Briefing ──────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "morning_briefing",
            "description": "Gives a complete morning briefing: time, battery, today's weather, and top news headlines — all spoken aloud. Use for 'good morning', 'subah ki briefing do', 'aaj ka update sunao'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City for weather (e.g. 'Delhi'). Leave empty for auto-detect."}
                },
                "required": []
            }
        }
    },

    # ── Smart Home ────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "smart_home",
            "description": "Controls smart home devices (TP-Link Kasa / Philips Hue). Use for 'light on karo', 'AC band karo', 'lights dim karo 50%'. Requires device IP in .env.",
            "parameters": {
                "type": "object",
                "properties": {
                    "device": {"type": "string", "description": "Device name: 'light', 'lights', 'ac', 'fan', 'plug', or specific device name"},
                    "action": {"type": "string", "enum": ["on", "off", "toggle", "dim", "status"], "description": "Action to perform"},
                    "value":  {"type": "integer", "description": "Brightness/intensity 0-100 (only for action='dim')"}
                },
                "required": ["device", "action"]
            }
        }
    },
]


# ─────────────────────────────────────────────────────────────────────────────
#  TOOL DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────

TOOL_DISPATCHER = {
    # ── File ops
    "find_files":             lambda a: tool_find_files(**a),
    "open_file_or_app":       lambda a: tool_open_file_or_app(**a),
    "read_file_snippet":      lambda a: tool_read_file_snippet(**a),
    "organize_folder":        lambda a: tool_organize_folder(**a),
    "safe_delete":            lambda a: tool_safe_delete(**a),
    "file_operation":         lambda a: tool_file_operation(**a),
    # ── Media
    "play_on_youtube":        lambda a: tool_play_on_youtube(**a),
    "play_on_spotify":        lambda a: tool_play_on_spotify(**a),
    # ── Web
    "open_website":           lambda a: tool_open_website(**a),
    "web_search":             lambda a: tool_web_search(**a),
    # ── WhatsApp
    "whatsapp_call":          lambda a: tool_whatsapp_call(**a),
    "whatsapp_message":       lambda a: tool_whatsapp_message(**a),
    # ── System
    "set_volume":             lambda a: tool_set_volume(**a),
    "take_screenshot":        lambda a: tool_take_screenshot(**a),
    "get_system_info":        lambda a: tool_get_system_info(**a),
    "set_timer":              lambda a: tool_set_timer(**a),
    "get_weather":            lambda a: tool_get_weather(**a),
    "quick_note":             lambda a: tool_quick_note(**a),
    "power_action":           lambda a: tool_power_action(**a),
    "clipboard_action":       lambda a: tool_clipboard_action(**a),
    "calculate":              lambda a: tool_calculate(**a),
    # ── Advanced
    "send_email":             lambda a: tool_send_email(**a),
    "read_emails":            lambda a: tool_read_emails(**a),
    "create_calendar_event":  lambda a: tool_create_calendar_event(**a),
    "open_multiple_apps":     lambda a: tool_open_multiple_apps(**a),
    "set_brightness":         lambda a: tool_set_brightness(**a),
    "wifi_control":           lambda a: tool_wifi_control(**a),
    "create_document":        lambda a: tool_create_document(**a),
    "get_news":               lambda a: tool_get_news(**a),
    "morning_briefing":       lambda a: tool_morning_briefing(**a),
    "smart_home":             lambda a: tool_smart_home(**a),
}


# ─────────────────────────────────────────────────────────────────────────────
#  SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are 'Aura', an intelligent, friendly, lightning-fast Voice OS Assistant for Windows.
Speak naturally like a real human assistant — conversational, warm, not robotic.
Your responses are read aloud via TTS — keep them SHORT (1-3 sentences), clear, and natural.
Understand Hindi/Hinglish commands perfectly (e.g. 'call karo', 'email bhejo', 'news sunao').

=== FULL CAPABILITY LIST ===

FILES & APPS:
  - Find files anywhere on PC (semantic + fuzzy search)
  - Open files, apps, websites
  - Copy / Move / Rename files
  - Read & summarize document contents
  - Organize Desktop/Downloads by file type
  - Safe delete to Recycle Bin

COMMUNICATION:
  - WhatsApp voice call (auto-clicks call button!)
  - WhatsApp video call
  - WhatsApp text message (auto-sends!)
  - Send Gmail email (body + subject)
  - Read & summarize Gmail inbox

MUSIC & MEDIA:
  - Play songs on YouTube (direct autoplay)
  - Play music on Spotify Desktop

NEWS & INFORMATION:
  - Latest news headlines (topic-wise: sports, tech, business, cricket, etc.)
  - Current weather for any city (free, no API key)
  - Morning briefing: time + battery + weather + news all at once
  - Google search anything

CALENDAR & REMINDERS:
  - Schedule meetings/events (opens in Windows Calendar/Outlook)
  - Set countdown timers with voice + popup alerts

DOCUMENTS:
  - Create Word (.docx) documents with content
  - Create Excel (.xlsx) spreadsheets with data

SYSTEM CONTROL:
  - Volume: set exact %, increase, decrease, mute, unmute
  - Brightness: set level, increase, decrease
  - Wi-Fi: status, list networks, connect, disconnect
  - Screenshot: save to Desktop
  - System info: CPU, RAM, battery, disk
  - Clipboard: copy / read / paste
  - Calculator: instant math
  - Quick notes: voice → saved text file

POWER:
  - Lock screen, sleep, shutdown, restart, cancel shutdown

SMART HOME:
  - TP-Link Kasa lights/plugs (requires IP in .env)
  - Philips Hue lights (requires Bridge IP in .env)

=== KEY RULES ===
1. WhatsApp CALL → use whatsapp_call (auto-clicks call button). VIDEO call → call_type='video'.
2. WhatsApp MESSAGE → use whatsapp_message (auto-types and sends!).
3. EMAIL → use send_email / read_emails. If not configured, tell user to set .env.
4. TIMER → ALWAYS convert to seconds: '5 min' = 300s, '1 hour' = 3600s, '45 min' = 2700s.
5. FILE OPS → First find_files to get path, then file_operation for copy/move/rename.
6. MULTIPLE APPS → use open_multiple_apps with a list. Don't call open_file_or_app separately.
7. MATH → always use calculate tool. Don't compute in your head.
8. NEVER delete without explicit user confirmation.
9. For WEATHER without city → pass empty string (auto-detects location).
10. For MORNING BRIEFING → use morning_briefing tool, not individual weather+news calls.
11. Hindi/Hinglish mappings: 'thoda badhao' = increase, 'band karo' = mute/off, 'kholo' = open,
    'bhejo' = send, 'sunao' = play/read, 'dikhai' = show, 'set karo' = set.
"""


# ─────────────────────────────────────────────────────────────────────────────
#  EXECUTE TOOL CALL
# ─────────────────────────────────────────────────────────────────────────────

def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    handler = TOOL_DISPATCHER.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        return handler(arguments)
    except Exception as e:
        return {"error": f"Tool '{tool_name}' failed: {str(e)}"}



# ─────────────────────────────────────────────────────────────────────────────
#  TOOL DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────

TOOL_DISPATCHER = {
    # File ops
    "find_files":       lambda a: tool_find_files(**a),
    "open_file_or_app": lambda a: tool_open_file_or_app(**a),
    "read_file_snippet":lambda a: tool_read_file_snippet(**a),
    "organize_folder":  lambda a: tool_organize_folder(**a),
    "safe_delete":      lambda a: tool_safe_delete(**a),
    # Media
    "play_on_youtube":  lambda a: tool_play_on_youtube(**a),
    "play_on_spotify":  lambda a: tool_play_on_spotify(**a),
    # Web
    "open_website":     lambda a: tool_open_website(**a),
    "web_search":       lambda a: tool_web_search(**a),
    # WhatsApp
    "whatsapp_call":    lambda a: tool_whatsapp_call(**a),
    "whatsapp_message": lambda a: tool_whatsapp_message(**a),
    # System
    "set_volume":       lambda a: tool_set_volume(**a),
    "take_screenshot":  lambda a: tool_take_screenshot(**a),
    "get_system_info":  lambda a: tool_get_system_info(**a),
    "set_timer":        lambda a: tool_set_timer(**a),
    "get_weather":      lambda a: tool_get_weather(**a),
    "quick_note":       lambda a: tool_quick_note(**a),
    "power_action":     lambda a: tool_power_action(**a),
    "clipboard_action": lambda a: tool_clipboard_action(**a),
    "calculate":        lambda a: tool_calculate(**a),
}


# ─────────────────────────────────────────────────────────────────────────────
#  SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are 'Aura', an intelligent, friendly, and lightning-fast Voice OS Assistant for Windows.
You speak naturally like a helpful human assistant — not robotic, not overly formal.
Your responses will be read aloud via Text-to-Speech, so keep them SHORT (1-3 sentences max), clear, and conversational.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 WHAT YOU CAN DO (Full List)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 FILES:         find files, open files, read & summarize documents, organize Desktop/Downloads, safely delete files
🎵 MUSIC:         play songs on YouTube (with autoplay), play on Spotify Desktop app
🌐 WEB:           open any website, Google search for anything
📱 WHATSAPP:      voice call a contact (auto-clicks call button!), video call, send text messages
🔊 VOLUME:        set exact volume %, increase, decrease, mute, unmute
📸 SCREENSHOT:    take and save a screenshot to Desktop
💻 SYSTEM:        CPU/RAM/battery/disk info
⏰ TIMER:         set countdown timers with voice reminder + popup
🌤️ WEATHER:       current weather for any city (free, no key needed)
📝 NOTES:         save a quick note to Desktop/AURA_Notes and open it
⚡ POWER:         lock screen, sleep, shutdown, restart, cancel shutdown
📋 CLIPBOARD:     copy text to clipboard, read clipboard, paste
🧮 CALCULATOR:    instantly calculate any math expression
🎵 SPOTIFY:       play music on Spotify Desktop app

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 KEY RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. For WhatsApp CALLS — use `whatsapp_call` tool. It auto-clicks the call button.
   For VIDEO calls — use `whatsapp_call` with call_type='video'.
   For MESSAGES — use `whatsapp_message` tool.

2. For TIMER — always convert to seconds before calling:
   "5 minutes" → seconds=300, "1 hour" → seconds=3600, "30 seconds" → seconds=30

3. For FILES — use `find_files` proactively. Users often don't know exact paths.
   If multiple files found, ask user: "I found 2 files — which one do you mean?"

4. For VOLUME — 'thoda' = up action, 'zyada' = up, 'kam' = down, 'band' = mute.

5. NEVER permanently delete without explicit user confirmation.

6. For MATH — use `calculate` tool for any arithmetic. Don't do math in your head.

7. Keep spoken responses natural and conversational. No bullet points, no markdown.

8. For WEATHER — if city not mentioned, use empty string (will auto-detect location).

9. For POWER actions — warn user before shutdown/restart with the delay time.
"""


# ─────────────────────────────────────────────────────────────────────────────
#  EXECUTE TOOL CALL
# ─────────────────────────────────────────────────────────────────────────────

def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    handler = TOOL_DISPATCHER.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}"}
    try:
        return handler(arguments)
    except Exception as e:
        return {"error": f"Tool '{tool_name}' failed: {str(e)}"}
