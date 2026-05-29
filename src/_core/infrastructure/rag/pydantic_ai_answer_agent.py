from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Final, LiteralString

import structlog
from pydantic import BaseModel, Field

from src._core.domain.dtos.rag import BaseChunkDTO, CitationDTO, QueryAnswerDTO
from src._core.exceptions.llm_exceptions import (
    GuardrailBlocked,
    PromptInjectionDetected,
)
from src._core.infrastructure.llm.guardrails import (
    detect_prompt_injection,
    find_prompt_leak,
    scan_pii,
)
from src._core.infrastructure.llm.prompt_boundaries import (
    RAG_INSTRUCTIONS_TAIL,
    escape_for_prompt_xml,
)

_logger = structlog.stdlib.get_logger(__name__)

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

    def __init__(self, llm_model: Any, *, guardrails_enabled: bool = True) -> None:
        try:
            from pydantic_ai import Agent
        except ImportError:
            raise ImportError(
                "pydantic-ai is required for the RAG answer agent. "
                "Install it with: uv sync --extra pydantic-ai"
            )

        self._guardrails_enabled = guardrails_enabled
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
        chunks = list(context_chunks)

        # Input guard (#197 Phase 3): block obvious prompt-injection imperatives
        # in the user question BEFORE calling the model. Only the question is
        # scanned — retrieved chunk content is DATA (already escaped in Phase
        # 1+2) and may legitimately quote trigger phrases.
        if self._guardrails_enabled:
            rule = detect_prompt_injection(question)
            if rule is not None:
                # rule name → structlog ONLY; never to the client response.
                _logger.warning("guardrail_triggered", stage="input", rule=rule)
                raise PromptInjectionDetected()

        prompt = _format_prompt(question, chunks)
        result = await self._agent.run(prompt)
        answer_text = result.output.answer

        # Output guard (#197 Phase 3).
        if self._guardrails_enabled:
            self._check_output(answer_text, chunks)

        citations = [CitationDTO.from_chunk(chunk) for chunk in chunks]
        return QueryAnswerDTO(answer=answer_text, citations=citations)

    def _check_output(self, answer_text: str, chunks: list[BaseChunkDTO]) -> None:
        """Block fabricated PII; log (do not block) verbatim prompt leaks.

        PII fabrication = PII in the answer that is absent from every chunk
        field that reaches the prompt (``source_title`` + ``content``). This is
        precise by construction (only invented PII is blocked), so it raises.
        Prompt leak is fuzzy (non-secret guidance may be paraphrased), so it is
        log-only.
        """
        context_pii: set[str] = set()
        for chunk in chunks:
            context_pii |= scan_pii(chunk.source_title)
            context_pii |= scan_pii(chunk.content)

        fabricated = scan_pii(answer_text) - context_pii
        if fabricated:
            # Count + token TYPES only — never the PII values themselves.
            types = sorted({token.split(":", 1)[0] for token in fabricated})
            _logger.warning(
                "guardrail_triggered",
                stage="output",
                rule="pii_fabrication",
                count=len(fabricated),
                types=types,
            )
            raise GuardrailBlocked()

        if find_prompt_leak(answer_text, _INSTRUCTIONS):
            _logger.warning("guardrail_triggered", stage="output", rule="prompt_leak")


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
