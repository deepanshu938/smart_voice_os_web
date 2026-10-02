import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import GROQ_API_KEY, GROQ_MODEL, GEMINI_API_KEY, GEMINI_MODEL, LLM_PROVIDER
from agent.llm_client import TOOLS_SCHEMA, SYSTEM_PROMPT, execute_tool_call

class AgentController:
    def __init__(self, provider: str = None):
        self.provider = (provider or LLM_PROVIDER).lower()
        self.messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self._init_client()

    def _init_client(self):
        self.groq_client = None
        self.active_model = GROQ_MODEL
        self.fallback_models = [
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "allam-2-7b"
        ]
        if self.provider == "groq":
            try:
                from groq import Groq
                if GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here":
                    self.groq_client = Groq(api_key=GROQ_API_KEY)
                    try:
                        # Auto-discover ONLY real conversational chat models
                        all_models = [m.id for m in self.groq_client.models.list().data]
                        
                        def is_real_chat_llm(name: str) -> bool:
                            nl = name.lower()
                            # Strictly reject safety guards, whisper audio, and terms-locked models
                            for blocked in ["guard", "whisper", "audio", "embed", "moderation", "safeguard", "orpheus"]:
                                if blocked in nl:
                                    return False
                            return True
                            
                        valid_chat = [m for m in all_models if is_real_chat_llm(m)]
                        
                        # Top verified chat models on user's Groq account
                        preferred_chat_order = [
                            "qwen/qwen3.8-27b",
                            "openai/gpt-oss-120b",
                            "openai/gpt-oss-20b",
                            "allam-2-7b"
                        ]
                        
                        # Rank models
                        prioritized = [p for p in preferred_chat_order if p in valid_chat]
                        remaining = [m for m in valid_chat if m not in prioritized]
                        final_models = prioritized + remaining
                        
                        if final_models:
                            self.active_model = final_models[0]
                            self.fallback_models = final_models
                            print(f"[Aura Engine]: Connected to Verified Groq Chat Model -> '{self.active_model}'")
                    except Exception as ex:
                        self.active_model = "qwen/qwen3.8-27b"
                        self.fallback_models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b"]
            except ImportError:
                self.groq_client = None

    def process_user_query(self, user_text: str) -> str:
        """Processes user input through LLM with function calling loop."""
        self.messages.append({"role": "user", "content": user_text})

        # Check if Groq client is active
        if self.groq_client:
            return self._run_groq_loop()
        else:
            return self._fallback_rule_engine(user_text)

    def _run_groq_loop(self) -> str:
        """Runs multi-turn Groq tool calling loop with resilient model fallback."""
        max_turns = 4
        current_turn = 0

        while current_turn < max_turns:
            current_turn += 1
            response = None
            
            # Attempt with current active model, fallback if model_not_found or decommissioned
            for model_candidate in [self.active_model] + [m for m in self.fallback_models if m != self.active_model]:
                try:
                    response = self.groq_client.chat.completions.create(
                        model=model_candidate,
                        messages=self.messages,
                        tools=TOOLS_SCHEMA,
                        tool_choice="auto",
                        temperature=0.2,
                        max_tokens=600
                    )
                    self.active_model = model_candidate
                    break
                except Exception as e:
                    err_msg = str(e).lower()
                    if any(k in err_msg for k in ["model_not_found", "does not exist", "404", "decommissioned", "not supported", "does not support", "model_decommissioned", "max_tokens"]):
                        continue  # Try next model candidate
                    return f"I encountered an API error: {str(e)}"
            
            if not response:
                return "Could not connect to any available Groq model. Please verify your Groq API key permissions."

            response_msg = response.choices[0].message
            tool_calls = response_msg.tool_calls

            if not tool_calls:
                # No more tools called; final response reached
                content = response_msg.content or "Done."
                self.messages.append({"role": "assistant", "content": content})
                return content

            # Append the assistant's decision to call tools to history
            self.messages.append(response_msg)

            # Execute all requested tool calls
            for tc in tool_calls:
                func_name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                except Exception:
                    args = {}
                
                result = execute_tool_call(func_name, args)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": func_name,
                    "content": json.dumps(result)
                })

        return "Task processed, but took too many steps."

    def _fallback_rule_engine(self, text: str) -> str:
        """Lightweight offline rule engine when API key is not yet set."""
        text_lower = text.lower()
        if "find" in text_lower or "dhundo" in text_lower or "search" in text_lower or "kahan" in text_lower or "where" in text_lower:
            from core.os_tools import tool_find_files
            words = [w for w in text_lower.split() if w not in {"find", "search", "dhundo", "file", "meri", "kahan", "hai", "the", "a"}]
            query = " ".join(words) or "document"
            res = tool_find_files(query=query)
            if res.get("status") == "found":
                first = res["candidates"][0]
                return f"I found '{first['name']}' in your files (Score: {first['score']}%). Full path: {first['path']}"
            return f"I searched your user folders, but couldn't find any file matching '{query}'. Please check .env to activate the full Groq LLM brain!"
        
        return "I heard you! Please paste your free GROQ_API_KEY in the .env file to enable full AI reasoning and function calling."
