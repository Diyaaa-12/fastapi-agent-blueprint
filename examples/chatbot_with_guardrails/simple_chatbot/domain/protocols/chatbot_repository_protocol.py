from typing import Protocol

from examples.chatbot_with_guardrails.domain.dtos.chatbot_dto import ChatMessageDTO
from src._core.domain.protocols.repository_protocol import BaseRepositoryProtocol


class ChatbotRepositoryProtocol(BaseRepositoryProtocol[ChatMessageDTO], Protocol):
    """Protocol for the chatbot message database operations."""

    pass
