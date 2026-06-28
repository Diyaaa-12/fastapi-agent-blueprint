from fastapi import FastAPI

from examples.chatbot_with_guardrails.infrastructure.di.chatbot_with_guardrails_container import (
    ChatbotWithGuardrailsContainer,
)
from examples.chatbot_with_guardrails.interface.server.routers import chatbot_router


def create_chatbot_with_guardrails_container(
    container: ChatbotWithGuardrailsContainer,
) -> None:
    """Wire dependencies into the chatbot-with-guardrails router package."""
    container.wire(
        packages=["examples.chatbot_with_guardrails.interface.server.routers"]
    )


def setup_chatbot_with_guardrails_routes(app: FastAPI) -> None:
    """Include chatbot-with-guardrails routes in the FastAPI app."""
    app.include_router(
        router=chatbot_router.router,
        prefix="/v1",
        tags=["ChatbotWithGuardrails"],
    )


def bootstrap_chatbot_with_guardrails_domain(
    app: FastAPI,
    container: ChatbotWithGuardrailsContainer,
) -> None:
    """Bootstrap the chatbot-with-guardrails example domain on the server."""
    create_chatbot_with_guardrails_container(container=container)
    setup_chatbot_with_guardrails_routes(app=app)
