# app/generators/chat_history_pdf_generator.py
"""Generador de PDF para el historial de conversación de Flash."""

import logging
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
from app.interfaces.i_chat_history_pdf_generator import IChatHistoryPdfGenerator
from app.entities.chat_message import ChatMessage

logger = logging.getLogger(__name__)

BOT_COLOR = (78, 43, 14)
USER_COLOR = (204, 85, 0)
BOT_BG_COLOR = (245, 235, 220)
USER_BG_COLOR = (255, 237, 217)


class ChatHistoryPdfGenerator(IChatHistoryPdfGenerator):
    """
    Genera un PDF con colores diferenciados para el historial de una conversación de Flash.

    Los mensajes del bot (Flash) se muestran con fondo beige y texto marrón oscuro.
    Los mensajes del usuario se muestran con fondo naranja claro y texto naranja oscuro.
    """

    def _render_timestamp(self, pdf: FPDF, timestamp: str) -> None:
        """Renderiza la fecha/hora en gris antes del bloque del mensaje."""
        try:
            dt = datetime.fromisoformat(timestamp).astimezone()
            formatted = dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            formatted = timestamp
        pdf.set_text_color(160, 160, 160)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 5, formatted, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def _format_user_message(self, pdf: FPDF, message: ChatMessage) -> None:
        """
        Renderiza una burbuja de mensaje del usuario en el PDF.

        Args:
            pdf: Instancia activa de FPDF.
            message: ChatMessage con role='user'.
        """
        self._render_timestamp(pdf, message.timestamp)
        pdf.set_fill_color(*USER_BG_COLOR)
        pdf.set_text_color(*USER_COLOR)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, "Usuario:", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, message.content, fill=True)
        pdf.ln(3)

    def _format_bot_message(self, pdf: FPDF, message: ChatMessage) -> None:
        """
        Renderiza una burbuja de mensaje de Flash (bot) en el PDF.

        Args:
            pdf: Instancia activa de FPDF.
            message: ChatMessage con role='assistant'.
        """
        self._render_timestamp(pdf, message.timestamp)
        pdf.set_fill_color(*BOT_BG_COLOR)
        pdf.set_text_color(*BOT_COLOR)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 7, "Flash:", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, message.content, fill=True)
        pdf.ln(3)

    def _build_pdf_layout(
        self,
        messages: list[ChatMessage],
        session_id: str,
    ) -> bytes:
        """
        Construye el PDF completo a partir de una lista de mensajes.

        Args:
            messages: Lista ordenada de objetos ChatMessage.
            session_id: Identificador de sesión mostrado en el encabezado.

        Returns:
            Archivo PDF como bytes en bruto.
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(*BOT_COLOR)
        pdf.cell(
            0, 12, "Historial de conversación con Flash",
            align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)
        export_ts = datetime.now().strftime("%d/%m/%Y %H:%M")
        pdf.cell(
            0, 6, f"Exportado: {export_ts}",
            align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        pdf.ln(6)

        for msg in messages:
            if msg.role == "user":
                self._format_user_message(pdf, msg)
            else:
                self._format_bot_message(pdf, msg)

        return bytes(pdf.output())

    def generate_pdf(
        self,
        messages: list[ChatMessage],
        session_id: str,
    ) -> bytes:
        """
        Genera un PDF del historial de la conversación.

        Args:
            messages: Lista ordenada de objetos ChatMessage.
            session_id: Identificador de sesión para el encabezado del PDF.

        Returns:
            Archivo PDF como bytes en bruto.
        """
        try:
            return self._build_pdf_layout(messages, session_id)
        except Exception as exc:
            logger.error("Generación del PDF del historial de chat falló: %s", exc)
            raise
