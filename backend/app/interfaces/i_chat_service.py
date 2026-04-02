# app/interfaces/i_chat_service.py
"""Interfaz abstracta para el servicio de chat."""

from abc import ABC, abstractmethod
from app.models.requests import ChatRequest
from app.models.responses import ChatResponse, ChatHistoryPdfResponse
from app.entities.chat_message import ChatMessage


class IChatService(ABC):
    """
    Clase base abstracta para el servicio conversacional de chat.

    Orquesta la clasificación de intención, generación de SQL, generación de respuestas con LLM,
    creación de gráficos y manejo de la memoria de la conversación.
    """

    @abstractmethod
    def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Procesa un mensaje del usuario y retorna la respuesta de Flash.

        Args:
            request: ChatRequest que contiene session_id y user_message.

        Returns:
            ChatResponse con bot_response y un chart_base64 opcional.
        """

    @abstractmethod
    def get_history(self, session_id: str) -> list[ChatMessage]:
        """
        Retorna el historial de conversación para la sesión dada.

        Args:
            session_id: Identificador único de la sesión de conversación.

        Returns:
            Lista ordenada de objetos ChatMessage.
        """

    @abstractmethod
    def export_history_pdf(self, session_id: str) -> ChatHistoryPdfResponse:
        """
        Exporta el historial de conversación como un archivo PDF.

        Args:
            session_id: Identificador único de la sesión de conversación.

        Returns:
            ChatHistoryPdfResponse con pdf_base64 y filename.
        """
