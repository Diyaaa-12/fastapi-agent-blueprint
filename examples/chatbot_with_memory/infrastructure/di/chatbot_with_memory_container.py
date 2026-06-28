from dependency_injector import containers, providers

from examples.chatbot_with_memory.domain.services.chatbot_memory_service import (
    ChatMemoryService,
)
from examples.chatbot_with_memory.infrastructure.chatbot.pydantic_ai_chatbot_memory import (
    PydanticAIChatbotMemory,
)
from examples.chatbot_with_memory.infrastructure.chatbot.stub_chatbot_memory import (
    StubChatbotMemory,
)
from examples.chatbot_with_memory.infrastructure.repositories.chatbot_memory_repository import (
    ChatbotMemoryRepository,
)
from src._core.config import settings


def _chatbot_selector() -> str:
    return "real" if settings.llm_model_name else "stub"


class ChatbotWithMemoryContainer(containers.DeclarativeContainer):
    """Dependency injection container for the chatbot-with-memory example domain."""

    core_container = providers.DependenciesContainer()

    chatbot_memory_repository = providers.Singleton(
        ChatbotMemoryRepository,
        database=core_container.database,
    )

    chatbot = providers.Selector(
        _chatbot_selector,
        real=providers.Singleton(
            PydanticAIChatbotMemory,
            llm_model=core_container.llm_model,
        ),
        stub=providers.Singleton(StubChatbotMemory),
    )

    chat_memory_service = providers.Factory(
        ChatMemoryService,
        chatbot=chatbot,
        repository=chatbot_memory_repository,
    )