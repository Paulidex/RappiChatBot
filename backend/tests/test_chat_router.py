# tests/test_chat_router.py
"""Integration tests for the chat router using FastAPI TestClient."""

import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.chat_router import ChatRouter
from app.models.responses import ChatResponse, ChatHistoryPdfResponse
from app.entities.chat_message import ChatMessage


def _build_app() -> tuple[FastAPI, MagicMock]:
    """Create a minimal FastAPI app with a mocked ChatService."""
    mock_service = MagicMock()
    mock_service.process_message.return_value = ChatResponse(
        session_id="test-session",
        bot_response="Hola, soy Flash",
        chart_base64=None,
        status_code=200,
    )
    mock_service.get_history.return_value = [
        ChatMessage(role="user", content="Hola"),
        ChatMessage(role="assistant", content="Hola, soy Flash"),
    ]
    mock_service.export_history_pdf.return_value = ChatHistoryPdfResponse(
        pdf_base64="base64pdf==",
        filename="flash_history_test-session.pdf",
    )

    router = ChatRouter(chat_service=mock_service)
    app = FastAPI()
    app.include_router(router.router, prefix="/api/v1")
    return app, mock_service


@pytest.fixture()
def client_and_service():
    app, service = _build_app()
    return TestClient(app), service


class TestChatRouter:
    """Integration tests for ChatRouter endpoints."""

    def test_post_message_returns_200(self, client_and_service):
        """POST /chat with a valid body should return 200."""
        client, _ = client_and_service
        response = client.post(
            "/api/v1/chat",
            json={"session_id": "test-session", "user_message": "Hola Flash"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["bot_response"] == "Hola, soy Flash"

    def test_post_message_empty_body_returns_400(self, client_and_service):
        """POST /chat with empty session_id should return 400."""
        client, _ = client_and_service
        response = client.post(
            "/api/v1/chat",
            json={"session_id": "", "user_message": ""},
        )
        assert response.status_code == 400

    def test_get_history_not_found_returns_404(self, client_and_service):
        """GET /chat/{session_id}/history for unknown session should return 404."""
        client, service = client_and_service
        service.get_history.return_value = []
        response = client.get("/api/v1/chat/unknown-session/history")
        assert response.status_code == 404

    def test_delete_session_returns_200(self, client_and_service):
        """DELETE /chat/{session_id} for an existing session should return 200."""
        client, _ = client_and_service
        response = client.delete("/api/v1/chat/test-session")
        assert response.status_code == 200

    def test_export_pdf_returns_200(self, client_and_service):
        """GET /chat/{session_id}/export-pdf should return 200 with pdf_base64."""
        client, _ = client_and_service
        response = client.get("/api/v1/chat/test-session/export-pdf")
        assert response.status_code == 200
        data = response.json()
        assert "pdf_base64" in data
        assert data["pdf_base64"] == "base64pdf=="
