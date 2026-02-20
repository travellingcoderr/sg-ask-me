"""
Factory that returns the correct LLM provider implementation based on configuration.
Add new providers here and set LLM_PROVIDER in env to switch (e.g. openai, gemini, anthropic).
"""
from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.openai_provider import OpenAIProvider

# Import Gemini provider conditionally (only if google-generativeai is installed)
try:
    from app.services.llm.gemini_provider import GeminiProvider
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False

_registry: dict[str, type[LLMProvider]] = {
    "openai": OpenAIProvider,
}

if _GEMINI_AVAILABLE:
    _registry["gemini"] = GeminiProvider


def get_llm_provider() -> LLMProvider:
    """Returns the configured LLM provider instance. Use this in routes instead of importing a concrete client."""
    key = (settings.LLM_PROVIDER or "openai").strip().lower()
    if key not in _registry:
        raise ValueError(
            f"Unknown LLM_PROVIDER={settings.LLM_PROVIDER!r}. "
            f"Supported: {list(_registry.keys())}"
        )
    return _registry[key]()


def register_provider(name: str, provider_class: type[LLMProvider]) -> None:
    """Register an additional provider (e.g. from app startup or tests)."""
    _registry[name.strip().lower()] = provider_class
