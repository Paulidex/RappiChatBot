# tests/test_chat_service.py
"""Unit tests for ChatService."""

import pytest
from unittest.mock import MagicMock, patch
from app.services.chat_service import ChatService
from app.services.conversation_memory import ConversationMemory
from app.entities.query_intent import QueryIntent
from app.entities.chat_message import ChatMessage
from app.models.requests import ChatRequest
from app.models.responses import ChatResponse, ChatHistoryPdfResponse


def _make_service(
    intent_type: str = "general",
    sql_data: list[dict] | None = None,
    chart_b64: str = "base64chart==",
    sql_raises: bool = False,
) -> tuple[ChatService, MagicMock, MagicMock, MagicMock, MagicMock, MagicMock]:
    """Helper that constructs a ChatService with mocked collaborators."""
    classifier = MagicMock()
    classifier.classify.return_value = QueryIntent(
        intent_type=intent_type,
        original_question="test question",
        extracted_filters={},
    )

    sql_generator = MagicMock()
    sql_generator.generate_sql.return_value = "SELECT 1"

    sql_executor = MagicMock()
    if sql_raises:
        sql_executor.execute.side_effect = Exception("DB error")
    else:
        sql_executor.execute.return_value = sql_data or [{"ZONE": "ZoneA", "value": 1}]

    response_generator = MagicMock()
    response_generator.generate.return_value = "Flash response text"

    chart_generator = MagicMock()
    chart_generator.generate_chart.return_value = chart_b64

    history_pdf_gen = MagicMock()
    history_pdf_gen.generate_pdf.return_value = b"%PDF-fake"

    memory = ConversationMemory(max_history=10)

    service = ChatService(
        classifier=classifier,
        sql_generator=sql_generator,
        sql_executor=sql_executor,
        response_generator=response_generator,
        chart_generator=chart_generator,
        memory=memory,
        history_pdf_gen=history_pdf_gen,
    )
    return service, classifier, sql_generator, sql_executor, response_generator, chart_generator


class TestChatService:
    """Unit tests for the ChatService class."""

    def test_chart_intent_generates_chart(self):
        """A 'chart' intent must produce a non-empty chart_base64 and bot_response."""
        service, *_ = _make_service(intent_type="chart")
        request = ChatRequest(session_id="s1", user_message="muestra gráfica de zonas")
        response = service.process_message(request)
        assert isinstance(response, ChatResponse)
        assert response.chart_base64 is not None
        assert response.chart_base64 != ""
        assert response.bot_response != ""

    def test_query_intent_returns_natural_language(self):
        """A 'query' intent must return a text response with no chart."""
        service, *_ = _make_service(intent_type="query")
        request = ChatRequest(session_id="s2", user_message="top 5 zonas")
        response = service.process_message(request)
        assert response.chart_base64 is None
        assert response.bot_response != ""

    def test_general_intent_responds_directly(self):
        """A 'general' intent must NOT call sql_generator or sql_executor."""
        service, classifier, sql_generator, sql_executor, *_ = _make_service(
            intent_type="general"
        )
        request = ChatRequest(session_id="s3", user_message="hola, ¿cómo te llamas?")
        response = service.process_message(request)
        sql_generator.generate_sql.assert_not_called()
        sql_executor.execute.assert_not_called()
        assert response.bot_response != ""

    def test_general_intent_uses_history(self):
        """build_context_prompt must be called for 'general' intent."""
        service, *_ = _make_service(intent_type="general")
        memory_mock = MagicMock(spec=ConversationMemory)
        memory_mock.get_history.return_value = [
            ChatMessage(role="user", content="pepito se llama Juan"),
            ChatMessage(role="assistant", content="Entendido"),
        ]
        memory_mock.build_context_prompt.return_value = (
            "Usuario: pepito se llama Juan\nFlash: Entendido"
        )
        service._memory = memory_mock

        request = ChatRequest(session_id="s4", user_message="¿cómo se llamaba pepito?")
        service.process_message(request)
        memory_mock.build_context_prompt.assert_called_once_with("s4")

    def test_invalid_sql_returns_error(self):
        """A SQL executor exception must be caught and return a status_code 500."""
        service, *_ = _make_service(intent_type="query", sql_raises=True)
        request = ChatRequest(session_id="s5", user_message="datos de zonas")
        response = service.process_message(request)
        assert response.status_code == 500
        assert "error" in response.bot_response.lower()

    def test_export_history_pdf(self):
        """export_history_pdf must return a ChatHistoryPdfResponse with pdf_base64."""
        service, *_ = _make_service(intent_type="general")
        request = ChatRequest(session_id="s6", user_message="hola")
        service.process_message(request)
        result = service.export_history_pdf("s6")
        assert isinstance(result, ChatHistoryPdfResponse)
        assert result.pdf_base64 != ""
        assert result.filename.endswith(".pdf")
