# app/services/chat_service.py
"""ChatService — orquesta la inteligencia conversacional de Flash."""

import base64
import logging
import os
from app.interfaces.i_chat_service import IChatService
from app.interfaces.i_intent_classifier import IIntentClassifier
from app.interfaces.i_sql_generator import ISqlGenerator
from app.interfaces.i_sql_executor import ISqlExecutor
from app.interfaces.i_response_generator import IResponseGenerator
from app.interfaces.i_chart_generator import IChartGenerator
from app.interfaces.i_chat_history_pdf_generator import IChatHistoryPdfGenerator
from app.services.conversation_memory import ConversationMemory
from app.entities.chat_message import ChatMessage
from app.entities.query_intent import QueryIntent
from app.models.requests import ChatRequest
from app.models.responses import ChatResponse, ChatHistoryPdfResponse

logger = logging.getLogger("chat")


class ChatService(IChatService):
    """
    Orquesta el flujo conversacional de Flash.

    Clasifica la intención del usuario, dirige la solicitud al manejador adecuado
    (chart / query / general), almacena los mensajes en memoria y
    retorna un ChatResponse estructurado.
    """

    def __init__(
        self,
        classifier: IIntentClassifier,
        sql_generator: ISqlGenerator,
        sql_executor: ISqlExecutor,
        response_generator: IResponseGenerator,
        chart_generator: IChartGenerator,
        memory: ConversationMemory,
        history_pdf_gen: IChatHistoryPdfGenerator,
    ) -> None:
        """
        Inicializa ChatService con sus colaboradores.

        Args:
            classifier: Clasificador de intención para enrutar mensajes.
            sql_generator: Convierte intenciones en consultas SQL.
            sql_executor: Ejecuta SQL contra la base de datos.
            response_generator: Genera respuestas en lenguaje natural.
            chart_generator: Genera gráficos en base64.
            memory: Almacenamiento del historial de conversación.
            history_pdf_gen: Exporta el historial de conversación como PDF.
        """
        self._classifier = classifier
        self._sql_generator = sql_generator
        self._sql_executor = sql_executor
        self._response_generator = response_generator
        self._chart_generator = chart_generator
        self._memory = memory
        self._history_pdf_gen = history_pdf_gen

    def _handle_chart_intent(self, intent: QueryIntent) -> tuple[str, str | None]:
        """
        Maneja una intención de tipo 'chart': genera explicación y gráfico.

        Args:
            intent: Intención clasificada con solicitud de gráfico.

        Returns:
            Tupla de (texto de respuesta del bot, cadena chart_base64 o None).
        """
        sql = self._sql_generator.generate_sql(intent)
        data = self._sql_executor.execute(sql)
        explanation = self._response_generator.generate(
            intent.original_question, data
        )
        chart = self._chart_generator.generate_chart(
            intent.original_question, data
        )
        return explanation, chart if chart else None

    def _handle_query_intent(self, intent: QueryIntent) -> tuple[str, None]:
        """
        Maneja una intención de tipo 'query': retorna datos solo en lenguaje natural.

        Args:
            intent: Intención clasificada con consulta de datos.

        Returns:
            Tupla de (texto de respuesta del bot, None).
        """
        sql = self._sql_generator.generate_sql(intent)
        data = self._sql_executor.execute(sql)
        explanation = self._response_generator.generate(
            intent.original_question, data
        )
        return explanation, None

    def _handle_general_intent(
        self, intent: QueryIntent, session_id: str
    ) -> tuple[str, None]:
        """
        Maneja una intención de tipo 'general': responde usando el historial de conversación.

        Args:
            intent: Intención general clasificada.
            session_id: Identificador de sesión para recuperar el historial.

        Returns:
            Tupla de (texto de respuesta del bot, None).
        """
        context = self._memory.build_context_prompt(session_id)
        full_question = (
            f"{context}\nUsuario: {intent.original_question}"
            if context
            else intent.original_question
        )
        text = self._response_generator.generate(full_question, data=[])
        return text, None

    def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Procesa un mensaje del usuario y retorna la respuesta de Flash.

        Clasifica la intención, enruta al manejador correcto y almacena tanto
        el mensaje del usuario como la respuesta de Flash en memoria.

        Args:
            request: ChatRequest que contiene session_id y user_message.

        Returns:
            ChatResponse con bot_response, chart_base64 opcional y
            preguntas sugeridas de seguimiento.
        """
        session_id = request.session_id
        user_message = request.user_message

        user_msg = ChatMessage(role="user", content=user_message)
        self._memory.add_message(session_id, user_msg)

        try:
            intent = self._classifier.classify(user_message)

            if intent.intent_type == "chart":
                bot_text, chart_b64 = self._handle_chart_intent(intent)
            elif intent.intent_type == "query":
                bot_text, chart_b64 = self._handle_query_intent(intent)
            else:
                bot_text, chart_b64 = self._handle_general_intent(
                    intent, session_id
                )

            bot_msg = ChatMessage(role="assistant", content=bot_text)
            self._memory.add_message(session_id, bot_msg)

            return ChatResponse(
                session_id=session_id,
                bot_response=bot_text,
                chart_base64=chart_b64,
                status_code=200,
            )
        except Exception as exc:
            logger.error("process_message failed for session %s: %s", session_id, exc)
            error_text = (
                "Lo siento, ocurrió un error al procesar tu mensaje. "
                "Por favor intenta de nuevo."
            )
            bot_msg = ChatMessage(
                role="assistant", content=error_text, message_type="error"
            )
            self._memory.add_message(session_id, bot_msg)
            return ChatResponse(
                session_id=session_id,
                bot_response=error_text,
                chart_base64=None,
                status_code=500,
            )

    def get_history(self, session_id: str) -> list[ChatMessage]:
        """
        Retorna el historial de conversación para la sesión indicada.

        Args:
            session_id: Identificador único de la sesión de conversación.

        Returns:
            Lista ordenada de objetos ChatMessage.
        """
        return self._memory.get_history(session_id)

    def export_history_pdf(self, session_id: str) -> ChatHistoryPdfResponse:
        """
        Exporta el historial de conversación como un archivo PDF.

        Args:
            session_id: Identificador único de la sesión de conversación.

        Returns:
            ChatHistoryPdfResponse con pdf_base64 y filename.

        Raises:
            ValueError: Si la sesión no tiene mensajes.
        """
        messages = self._memory.get_history(session_id)
        if not messages:
            raise ValueError(f"No history found for session '{session_id}'.")
        pdf_bytes = self._history_pdf_gen.generate_pdf(messages, session_id)
        filename = f"flash_history_{session_id}.pdf"
        pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "pdf")
        os.makedirs(pdf_dir, exist_ok=True)
        with open(os.path.join(pdf_dir, filename), "wb") as f:
            f.write(pdf_bytes)
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        return ChatHistoryPdfResponse(pdf_base64=pdf_b64, filename=filename)
