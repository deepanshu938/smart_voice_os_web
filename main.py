import sys
import os
# Fix Windows console Unicode issues
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

from config import GROQ_API_KEY, LLM_PROVIDER, GROQ_MODEL
from agent.agent_controller import AgentController
from voice.tts import TextToSpeechEngine
from voice.stt import SpeechToTextEngine

def print_banner():
    banner = """
  +======================================================================+
  |             *  AURA  --  SMART VOICE OS ASSISTANT  *                |
  |                                                                      |
  |  Files & Apps      YouTube & Spotify       Web Search               |
  |  WhatsApp Call/Msg    Volume Control        Screenshot              |
  |  System Info       Timer & Alarm            Weather                 |
  |  Quick Notes       Power Actions            Clipboard  Calc         |
  |                                                                      |
  |  Powered by Groq  *  100% Free  *  Voice + Text Mode               |
  +======================================================================+
    """
    print(banner)


def run_self_test():
    """Runs a quick verification test on the file resolver."""
    print("\n--- Running Smart Search Self-Test ---")
    from core.file_resolver import scan_file_system
    print("Testing search across user folders...")
    results = scan_file_system(query="bill", max_results=3)
    print(f"Results found: {len(results)}")
    for r in results:
        print(f"  • {r['name']} (Score: {r['score']}%) -> {r['reason']}")
    print("Self-test completed successfully!\n")

def main():
    print_banner()

    agent = AgentController()
    tts = TextToSpeechEngine()
    stt = SpeechToTextEngine()

    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        print("[!] Note: GROQ_API_KEY not found in .env. Running in offline rule mode.")
        print("    Add your free key to .env to unlock full 70B reasoning & function calling.\n")
    else:
        print(f"[✓] Active LLM Provider: Groq ({GROQ_MODEL}) [Free Tier]\n")

    print("Choose an interaction mode:")
    print("  [1] Voice Mode (Speak with your Microphone)")
    print("  [2] Text Mode (Type commands - fast & quiet)")
    print("  [3] Run Search Diagnostic Test")
    print("  [q] Quit")

    choice = input("\nEnter choice (1/2/3/q) [Default: 2]: ").strip() or "2"

    if choice == "3":
        run_self_test()
        return

    if choice.lower() == "q":
        print("Goodbye!")
        return

    mode = "voice" if choice == "1" else "text"
    print(f"\n[✓] Started in {mode.upper()} mode. Type or say 'quit' to exit.\n")
    tts.speak("Smart Voice OS Assistant is ready.")

    while True:
        try:
            if mode == "voice":
                input("\n[Press ENTER to start speaking...]")
                user_input = stt.listen_and_transcribe()
                if not user_input:
                    continue
            else:
                user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in {"quit", "exit", "bye", "stop", "q", "[q]"}:
                tts.speak("Goodbye! Have a productive day.")
                break

            # Process through agent
            print(f"\n[Aura is processing...]")
            response = agent.process_user_query(user_input)
            
            # Speak and print response
            tts.speak(response)

        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"\n[Error]: {str(e)}")

if __name__ == "__main__":
    main()
