from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Validation schema for chat request body."""

    prompt: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The user prompt/message to the chatbot",
    )


class ChatResponse(BaseModel):
    """Serialization schema for chatbot response (with tokens_used for educational visibility)."""

    reply: str = Field(..., description="The generated response from the chatbot")
    confidence: float = Field(
        ..., description="Confidence score of the structured output model"
    )
    tokens_used: int = Field(
        ..., description="Calculated total token usage (input + output)"
    )


class ChatHistoryResponse(BaseModel):
    """Serialization schema for retrieved historical chatbot messages."""

    id: int = Field(..., description="The database primary key")
    prompt: str = Field(..., description="The original user prompt")
    reply: str = Field(..., description="The historical chatbot reply")
    tokens_used: int = Field(
        ..., description="Number of tokens used in that generation"
    )
    created_at: datetime = Field(
        ..., description="The date/time the message was persisted"
    )
