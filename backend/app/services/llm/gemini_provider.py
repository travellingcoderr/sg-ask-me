"""
Google Gemini implementation of the LLM provider interface.
Uses the Gemini API to stream chat responses.
"""
from typing import Any, Iterator
import google.generativeai as genai
from app.core.config import settings
from app.services.llm.base import LLMProvider, LLMChatStream, StreamEvent


class _GeminiStreamAdapter:
    """Wraps Gemini stream and yields normalized StreamEvent (delta / done)."""

    def __init__(self, gemini_stream: Any) -> None:
        self._stream = gemini_stream
        self._response_id: str | None = None

    def __enter__(self) -> "_GeminiStreamAdapter":
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def __iter__(self) -> Iterator[StreamEvent]:
        full_text = ""
        for chunk in self._stream:
            if chunk.text:
                full_text += chunk.text
                yield StreamEvent(kind="delta", text=chunk.text)
            # Gemini doesn't provide response_id in the same way, generate one if needed
            if chunk.candidates and chunk.candidates[0].finish_reason:
                # Use a simple hash or timestamp as response_id
                import hashlib
                self._response_id = hashlib.md5(full_text.encode()).hexdigest()[:16]
                yield StreamEvent(kind="done", response_id=self._response_id)
                break


class GeminiProvider:
    """Implements LLMProvider using Google Gemini API."""

    def __init__(self) -> None:
        api_key = getattr(settings, "GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in environment variables")
        genai.configure(api_key=api_key)
        
        # List available models for debugging
        # Note: Free tier API keys may have limited model access
        try:
            models_list = genai.list_models()
            available_models = []
            for m in models_list:
                if 'generateContent' in m.supported_generation_methods:
                    model_name = m.name.replace('models/', '')
                    available_models.append(model_name)
            self._available_models = available_models
            if available_models:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Available Gemini models: {', '.join(available_models)}")
        except Exception as e:
            # If listing fails, use defaults
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not list Gemini models: {e}. Using defaults.")
            self._available_models = []

    def stream_chat(
        self,
        model: str,
        input_items: list[dict[str, Any]],
        previous_response_id: str | None = None,
    ) -> LLMChatStream:
        # Convert input_items format to Gemini's expected format
        # Gemini expects a list of Content objects or a simple string
        # For chat, we'll use the chat history format
        
        # Extract system message if present
        system_instruction = None
        messages = []
        for item in input_items:
            role = item.get("role", "")
            content = item.get("content", "")
            if role == "system":
                system_instruction = content
            elif role in ("user", "assistant"):
                messages.append({"role": role, "parts": [content]})
        
        # Use Gemini's chat model
        # Default to free tier model if not specified
        # Try common model names in order of preference
        gemini_model_name = model
        if not gemini_model_name:
            # Try free tier models first, then fallback to others
            preferred_models = [
                "gemini-3-flash-preview",  # Latest free tier
                "gemini-1.5-flash",       # Older free tier
                "gemini-1.5-pro",         # Pro version
                "gemini-2.0-flash",       # 2.0 version
            ]
            # Use first available model, or first in list if we can't check
            if self._available_models:
                for preferred in preferred_models:
                    if preferred in self._available_models:
                        gemini_model_name = preferred
                        break
                if not gemini_model_name:
                    gemini_model_name = self._available_models[0] if self._available_models else preferred_models[0]
            else:
                gemini_model_name = preferred_models[0]
        
        try:
            gemini_model = genai.GenerativeModel(
                model_name=gemini_model_name,
                system_instruction=system_instruction,
            )
        except Exception as e:
            # Provide helpful error message with available models
            available_msg = f" Available models: {', '.join(self._available_models)}" if self._available_models else ""
            raise ValueError(
                f"Model '{gemini_model_name}' not found or not available.{available_msg}\n"
                f"Set LLM_MODEL in .env to one of the available models."
            ) from e
        
        # Start chat session (Gemini handles conversation history)
        chat = gemini_model.start_chat(history=messages[:-1] if len(messages) > 1 else [])
        
        # Get the last user message
        last_message = messages[-1]["parts"][0] if messages else ""
        
        # Stream the response
        response = chat.send_message(last_message, stream=True)
        
        return _GeminiStreamAdapter(response)
