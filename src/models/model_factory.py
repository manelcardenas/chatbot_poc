import os

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.tracers.langchain import LangChainTracer
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_deepseek import ChatDeepSeek
from langchain_google_gemini import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from src.models.model_names import ModelName, ModelProvider


class ModelFactory:
    """Factory for creating and managing language model instances."""

    def __init__(self) -> None:
        """Initialize the model factory."""
        self.callbacks: CallbackManager = CallbackManager([])
        self.tracer: LangChainTracer = None
        if os.getenv("ENABLE_LANGSMITH_TRACKING", "false").lower() == "true":
            self.tracer = LangChainTracer(project_name=os.getenv("LANGCHAIN_PROJECT"))
            self.callbacks = CallbackManager([self.tracer])
        self._providers: dict[ModelProvider, callable[[ModelName], BaseChatModel]] = {
            ModelProvider.OPENAI: self._create_openai_model,
            ModelProvider.ANTHROPIC: self._create_anthropic_model,
            ModelProvider.DEEPSEEK: self._create_deepseek_model,
            ModelProvider.OLLAMA: self._create_ollama_model,
            ModelProvider.GEMINI: self._create_gemini_model,
        }

    def get_model(self, model: ModelProvider, model_name: ModelName | None) -> BaseChatModel:
        """Get a model instance based on provider."""
        create_fn = self._providers.get(model)
        if create_fn is None:
            raise ValueError(f"Unsupported model provider: {model}")
        return create_fn(model_name)

    def _create_openai_model(self, model_name: ModelName) -> BaseChatModel:
        return ChatOpenAI(
            model=model_name.value if model_name else ModelName.GPT_4O_MINI.value, callbacks=self.callbacks
        )

    def _create_anthropic_model(self, model_name: ModelName) -> BaseChatModel:
        return ChatAnthropic(
            model=model_name.value if model_name else ModelName.CLAUDE_3_5_SONNET.value, callbacks=self.callbacks
        )

    def _create_deepseek_model(self, model_name: ModelName) -> BaseChatModel:
        return ChatDeepSeek(
            model=model_name.value if model_name else ModelName.DEEPSEEK_V3.value, callbacks=self.callbacks
        )

    def _create_ollama_model(self, model_name: ModelName) -> BaseChatModel:
        return ChatOllama(
            model=model_name.value if model_name else ModelName.QWEN2_5_14B.value, callbacks=self.callbacks
        )

    def _create_gemini_model(self, model_name: ModelName) -> BaseChatModel:
        return ChatGoogleGenerativeAI(
            model=model_name.value if model_name else ModelName.GEMINI_1_5_PRO.value, callbacks=self.callbacks
        )
