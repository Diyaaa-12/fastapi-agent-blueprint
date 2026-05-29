from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Final, LiteralString

from pydantic import BaseModel, Field

from src._core.domain.dtos.rag import BaseChunkDTO, CitationDTO, QueryAnswerDTO
from src._core.infrastructure.llm.prompt_boundaries import (
    RAG_INSTRUCTIONS_TAIL,
    escape_for_prompt_xml,
)

_PERSONA: Final[LiteralString] = (
    "You are a precise RAG assistant. "
    "Answer the user's question using ONLY the provided context chunks. "
    "Cite sources as [source_title]. "
    "If the context doesn't contain the answer, say so plainly."
)

# Concatenation of two ``LiteralString`` values is itself ``LiteralString``,
# so static analysis (``uv run pyright``) blocks any future f-string that
# would interpolate untrusted runtime data into the agent's behavioural
# contract. The boundary-tag wrapping in ``_format_prompt`` is what
# actually mitigates LLM01; this constant is the matching "treat the
# wrapped content as untrusted DATA" guidance for the model.
_INSTRUCTIONS: Final[LiteralString] = _PERSONA + RAG_INSTRUCTIONS_TAIL


class _AgentAnswer(BaseModel):
    """Structured output requested from the LLM.

    Citations are assembled deterministically from the retrieval result
    (see ``PydanticAIAnswerAgent.answer``) rather than fabricated by the
    model, so the agent is asked only for the answer text.
    """

    answer: str = Field(..., description="The answer text")


class PydanticAIAnswerAgent:
    """Real LLM-backed RAG answerer via PydanticAI."""

    def __init__(self, llm_model: Any) -> None:
        try:
            from pydantic_ai import Agent
        except ImportError:
            raise ImportError(
                "pydantic-ai is required for the RAG answer agent. "
                "Install it with: uv sync --extra pydantic-ai"
            )

        self._agent: Agent[None, _AgentAnswer] = Agent(
            model=llm_model,
            output_type=_AgentAnswer,
            instructions=_INSTRUCTIONS,
        )

    async def answer(
        self,
        question: str,
        context_chunks: Sequence[BaseChunkDTO],
    ) -> QueryAnswerDTO:
        prompt = _format_prompt(question, list(context_chunks))
        result = await self._agent.run(prompt)
        citations = [CitationDTO.from_chunk(chunk) for chunk in context_chunks]
        return QueryAnswerDTO(answer=result.output.answer, citations=citations)


def _format_prompt(question: str, chunks: list[BaseChunkDTO]) -> str:
    """Compose the user-turn payload with XML-bounded, escape-safe wrapping.

    Every dynamic field (chunk title, chunk content, user question) goes
    through :func:`escape_for_prompt_xml`. ``index`` is integer-formatted
    so it cannot host injection. ``<title>`` / ``<content>`` are child
    elements (not attributes) so an attribute-quote breakout
    (``title=""onload="``) is impossible.

    A literal ``</document>`` inside chunk content is escaped to
    ``&lt;/document&gt;`` and therefore cannot close the surrounding
    boundary in the model's parse — verified by the adversarial fixtures
    in ``test_pydantic_ai_answer_agent_prompt.py``.
    """
    escaped_question = escape_for_prompt_xml(question)
    if not chunks:
        return f"<documents />\n<user_question>{escaped_question}</user_question>"

    docs_xml = "\n".join(
        f'<document index="{i + 1}">'
        f"<title>{escape_for_prompt_xml(chunk.source_title)}</title>"
        f"<content>{escape_for_prompt_xml(chunk.content)}</content>"
        f"</document>"
        for i, chunk in enumerate(chunks)
    )
    return (
        f"<documents>\n{docs_xml}\n</documents>\n"
        f"<user_question>{escaped_question}</user_question>"
    )
