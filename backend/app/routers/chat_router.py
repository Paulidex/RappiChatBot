# app/routers/chat_router.py
"""Router de FastAPI para los endpoints conversacionales de Flash."""

import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.interfaces.i_chat_service import IChatService
from app.models.requests import ChatRequest
from app.models.responses import ChatResponse
from app.entities.chat_message import ChatMessage

logger = logging.getLogger(__name__)


class ChatRouter:
    """
    Expone los endpoints conversacionales de Flash bajo /chat.

    Endpoints:
        POST   /chat                         — enviar un mensaje
        GET    /chat/{session_id}/history    — obtener el historial de conversación
        GET    /chat/{session_id}/export-pdf — exportar el historial como PDF
    """

    def __init__(self, chat_service: IChatService) -> None:
        """
        Inicializa el router de chat con su dependencia de servicio.

        Args:
            chat_service: Implementación de IChatService.
        """
        self._chat_service = chat_service
        self.router = APIRouter(tags=["Chat"])
        self._register_routes()

    def _register_routes(self) -> None:
        """Registra todos los manejadores de rutas en self.router."""
        self.router.add_api_route(
            "/chat",
            self.post_message,
            methods=["POST"],
            response_model=ChatResponse,
            status_code=200,
        )
        self.router.add_api_route(
            "/chat/{session_id}/history",
            self.get_chat_history,
            methods=["GET"],
            response_model=list[dict],
            status_code=200,
        )
        self.router.add_api_route(
            "/chat/{session_id}/export-pdf",
            self.export_history_pdf,
            methods=["GET"],
            status_code=200,
        )

    async def post_message(self, request: ChatRequest) -> ChatResponse:
        """
        Procesa un mensaje del usuario y retorna la respuesta de Flash.

        Args:
            request: ChatRequest con session_id y user_message.

        Returns:
            ChatResponse con la respuesta del bot y un gráfico opcional.

        Raises:
            HTTPException 400: Si el cuerpo de la solicitud carece de campos requeridos.
            HTTPException 500: En errores inesperados de procesamiento.
        """
        if not request.session_id or not request.user_message:
            raise HTTPException(
                status_code=400,
                detail="session_id and user_message are required.",
            )
        try:
            return self._chat_service.process_message(request)
        except Exception as exc:
            logger.error("POST /chat error: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))

    async def get_chat_history(self, session_id: str) -> list[dict]:
        """
        Retorna el historial de conversación para la sesión indicada.

        Args:
            session_id: Identificador de sesión desde la URL.

        Returns:
            Lista de diccionarios de mensajes.

        Raises:
            HTTPException 404: Si no existen mensajes para la sesión.
        """
        history: list[ChatMessage] = self._chat_service.get_history(session_id)
        if not history:
            raise HTTPException(
                status_code=404,
                detail=f"No history found for session '{session_id}'.",
            )
        return [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp,
                "message_type": m.message_type,
            }
            for m in history
        ]

    async def export_history_pdf(self, session_id: str) -> Response:
        """
        Exporta el historial de conversación como un archivo PDF descargable.

        Args:
            session_id: Identificador de sesión desde la URL.

        Returns:
            Respuesta HTTP con el PDF como archivo adjunto.

        Raises:
            HTTPException 404: Si no existen mensajes para la sesión.
        """
        try:
            pdf_response = self._chat_service.export_history_pdf(session_id)
            import base64  # noqa: PLC0415
            pdf_bytes = base64.b64decode(pdf_response.pdf_base64)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f"inline; filename={pdf_response.filename}"},
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))
        except Exception as exc:
            logger.error("export-pdf error: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))
