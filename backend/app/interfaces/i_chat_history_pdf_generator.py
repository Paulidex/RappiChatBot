# app/interfaces/i_chat_history_pdf_generator.py
"""Interfaz abstracta para la generación de PDFs del historial de chat."""

from abc import ABC, abstractmethod
from app.entities.chat_message import ChatMessage


class IChatHistoryPdfGenerator(ABC):
    """
    Clase base abstracta para exportar el historial de conversación a PDF.

    Las implementaciones generan un documento PDF con estilo y mensajes
    codificados por colores para el usuario y el bot Flash.
    """

    @abstractmethod
    def generate_pdf(
        self,
        messages: list[ChatMessage],
        session_id: str,
    ) -> bytes:
        """
        Genera un PDF a partir de una lista de mensajes de chat.

        Args:
            messages: Lista ordenada de objetos ChatMessage.
            session_id: Identificador de sesión mostrado en el encabezado del PDF.

        Returns:
            Contenido del archivo PDF como bytes en bruto.
        """
