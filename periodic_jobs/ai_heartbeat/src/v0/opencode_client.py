import requests
import json
import base64
import os
import time
from pathlib import Path
from dotenv import load_dotenv

module_dir = Path(__file__).resolve().parent
project_env_path = module_dir.parent.parent / ".env"
legacy_env_path = module_dir.parent / ".env"
if project_env_path.exists():
    load_dotenv(project_env_path)
else:
    load_dotenv(legacy_env_path)

# Message timeout: agentic tasks can run 10–60+ min. Default 1 hour.
MESSAGE_TIMEOUT = int(os.getenv("OPENCODE_MESSAGE_TIMEOUT", "3600"))

class OpenCodeClient:
    def __init__(self):
        self.base_url = os.getenv("OPENCODE_BASE_URL", "http://localhost:4096")
        self.username = os.getenv("OPENCODE_USERNAME", "opencode")
        self.password = os.getenv("OPENCODE_PASSWORD") or os.getenv("OPENCODE_SERVER_PASSWORD")
        
        if not self.password:
            raise ValueError("OPENCODE_PASSWORD not found in environment variables.")
            
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
        }
        
        self._default_model = os.getenv("OPENCODE_DEFAULT_MODEL", "MiniMax-M2.7")
        self._default_provider = os.getenv("OPENCODE_DEFAULT_PROVIDER", "Friday-Cheap")
        self._default_model = os.getenv("OPENCODE_DEFAULT_MODEL", "MiniMax-M2.7")
        self._default_provider = os.getenv("OPENCODE_DEFAULT_PROVIDER", "Friday-Cheap")
        
    def _create_session_via_api(self, title):
        """Create session using API. Note: API-created sessions may not receive messages properly."""
        try:
            response = requests.post(
                f"{self.base_url}/session",
                json={"title": title},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()['id']
        except Exception as e:
            print(f"Error creating session: {e}")
            return None
    
    def _create_session_via_fork(self, parent_session_id, parent_message_id):
        """Create session by forking from a working session. This always works."""
        try:
            response = requests.post(
                f"{self.base_url}/session/{parent_session_id}/fork",
                json={"messageID": parent_message_id} if parent_message_id else {},
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()['id']
        except Exception as e:
            print(f"Error forking session: {e}")
            return None

    def create_session(self, title, parent_session_id=None, parent_message_id=None):
        """
        Create a new session.
        
        If parent_session_id is provided, forks from that session (recommended).
        Otherwise creates via API (may have issues receiving messages).
        """
        if parent_session_id:
            return self._create_session_via_fork(parent_session_id, parent_message_id)
        return self._create_session_via_api(title)

    def list_sessions(self):
        """GET /session - list all sessions."""
        try:
            response = requests.get(
                f"{self.base_url}/session",
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []

    def send_message(self, session_id, message, model_id=None, provider_id=None, agent="OpenCode-Builder"):
        """
        Send a message to a session.
        
        If model_id/provider_id not specified, uses defaults from env or MiniMax-M2.7/Friday-Cheap.
        """
        try:
            # Auto-detect provider from model_id if not specified
            if provider_id is None:
                if model_id and "/" in model_id:
                    provider_id, model_id = model_id.split("/", 1)
                elif model_id:
                    # Assume if model_id looks like a provider/model format, split it
                    if model_id.startswith(("anthropic", "google", "openai", "Friday")):
                        parts = model_id.split("/", 1)
                        if len(parts) == 2:
                            provider_id, model_id = parts
                        else:
                            provider_id = self._default_provider
                    else:
                        provider_id = self._default_provider
                else:
                    provider_id = self._default_provider
                    model_id = self._default_model
            
            if model_id is None:
                model_id = self._default_model

            payload = {
                "parts": [{"type": "text", "text": message}]
            }
            
            response = requests.post(
                f"{self.base_url}/session/{session_id}/message",
                json=payload,
                headers=self.headers,
                timeout=MESSAGE_TIMEOUT,
            )
            
            if response.status_code != 200:
                print(f"Server returned {response.status_code} Error: {response.text}")
                response.raise_for_status()

            # Handle empty response - this is normal for async processing
            if not response.text.strip():
                return {
                    "status": "accepted_empty_response",
                    "session_id": session_id,
                }

            try:
                return response.json()
            except ValueError:
                print(f"Response JSON parse failed: {response.text[:200]!r}")
                return None
                
        except requests.exceptions.RequestException as e:
            if "Read timed out" not in str(e):
                print(f"Request Exception: {e}")
            return None

    def prompt_async(self, session_id, message, provider_id=None, model_id=None, agent=None):
        if provider_id is None and model_id and "/" in model_id:
            provider_id, model_id = model_id.split("/", 1)
        payload = {"parts": [{"type": "text", "text": message}]}
        if agent:
            payload["agent"] = agent
        if provider_id:
            payload["providerID"] = provider_id
        if model_id:
            payload["modelID"] = model_id
        try:
            response = requests.post(
                f"{self.base_url}/session/{session_id}/prompt_async",
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            return response.status_code == 204
        except Exception as e:
            print(f"Error calling prompt_async: {e}")
            return False

    def init_session(self, session_id, message_id, model_id=None, provider_id=None):
        if provider_id is None and model_id and "/" in model_id:
            provider_id, model_id = model_id.split("/", 1)
        if model_id is None:
            model_id = self._default_model
        if provider_id is None:
            provider_id = self._default_provider
        try:
            response = requests.post(
                f"{self.base_url}/session/{session_id}/init",
                json={"modelID": model_id, "providerID": provider_id, "messageID": message_id},
                headers=self.headers,
                timeout=MESSAGE_TIMEOUT,
            )
            response.raise_for_status()
            return True
        except requests.exceptions.ReadTimeout:
            return True
        except Exception as e:
            print(f"Error calling /init: {e}")
            return False

    def get_session_messages(self, session_id):
        """Get all messages in a session."""
        try:
            response = requests.get(
                f"{self.base_url}/session/{session_id}/message",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting messages: {e}")
            return None

    def get_session_info(self, session_id):
        """GET /session/:id - session metadata."""
        try:
            response = requests.get(
                f"{self.base_url}/session/{session_id}",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting session info: {e}")
            return None

    def delete_session(self, session_id):
        """DELETE /session/:id - remove session."""
        try:
            response = requests.delete(
                f"{self.base_url}/session/{session_id}",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False

    def wait_for_session_complete(
        self,
        session_id,
        poll_interval=15,
        max_wait=7200,
    ):
        """
        Poll until session is idle.
        """
        start = time.time()
        while (time.time() - start) < max_wait:
            messages = self.get_session_messages(session_id)
            if messages and len(messages) > 0:
                last_msg = messages[-1]
                if isinstance(last_msg, dict):
                    role = last_msg.get("info", {}).get("role")
                    if role == "assistant":
                        finish = last_msg.get("info", {}).get("finish")
                        if finish == "stop":
                            return True
            elapsed = int(time.time() - start)
            print(f"  ... waiting ({elapsed}s elapsed), polling in {poll_interval}s")
            time.sleep(poll_interval)
        print(f"  wait_for_session_complete: max_wait {max_wait}s exceeded")
        return False
