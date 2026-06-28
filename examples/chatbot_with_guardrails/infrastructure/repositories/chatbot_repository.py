from examples.chatbot_with_guardrails.domain.dtos.chatbot_dto import ChatMessageDTO
from examples.chatbot_with_guardrails.domain.protocols.chatbot_repository_protocol import (
    ChatbotRepositoryProtocol,
)
from examples.chatbot_with_guardrails.infrastructure.database.models.chatbot_model import (
    ChatMessageModel,
)
from src._core.infrastructure.persistence.rdb.base_repository import BaseRepository
from src._core.infrastructure.persistence.rdb.database import Database


class ChatbotRepository(BaseRepository[ChatMessageDTO], ChatbotRepositoryProtocol):
    """Database repository for persisting and retrieving chatbot messages."""

    def __init__(self, database: Database) -> None:
        super().__init__(
            database=database,
            model=ChatMessageModel,
            return_entity=ChatMessageDTO,
        )
