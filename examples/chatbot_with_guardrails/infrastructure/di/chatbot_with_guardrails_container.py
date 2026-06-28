from dependency_injector import containers, providers
from examples.chatbot_with_guardrails.domain.services.chatbot_service import ChatService
from examples.chatbot_with_guardrails.infrastructure.chatbot.pydantic_ai_chatbot import PydanticAIChatbot
from examples.chatbot_with_guardrails.infrastructure.chatbot.stub_chatbot import StubChatbot
from examples.chatbot_with_guardrails.infrastructure.repositories.chatbot_repository import ChatbotRepository
from src._core.config import settings


def _chatbot_selector() -> str:
    return "real" if settings.llm_model_name else "stub"


class ChatbotWithGuardrailsContainer(containers.DeclarativeContainer):
    """Dependency injection container for the chatbot-with-guardrails example domain."""
    core_container = providers.DependenciesContainer()

    chatbot_repository = providers.Singleton(
        ChatbotRepository,
        database=core_container.database,
    )

    chatbot = providers.Selector(
        _chatbot_selector,
        real=providers.Singleton(
            PydanticAIChatbot,
            llm_model=core_container.llm_model,
            guardrails_enabled=True,
        ),
        stub=providers.Singleton(
            StubChatbot,
            guardrails_enabled=True,
        ),
    )

    chat_service = providers.Factory(
        ChatService,
        chatbot=chatbot,
        repository=chatbot_repository,
    )
