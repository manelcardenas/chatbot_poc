from enum import Enum


class ModelProvider(Enum):
    """Supported language model providers."""

    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    GEMINI = "google-genai"


class ModelName(Enum):
    """Supported model names for each provider."""

    # OpenAI
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    # Anthropic
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet"
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"
    # DeepSeek
    DEEPSEEK_V3 = "deepseek-chat"
    # Ollama models
    QWEN2_5_14B = "qwen2.5:14b"
    DEEPSEEK_R1_14B = "deepseek-r1:14b"
    # Gemini
    GEMINI_1_5_PRO = "gemini-1.5-pro"
