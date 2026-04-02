# app/services/conversation_memory.py
"""Gestor de historial de conversación en memoria para sesiones de Flash."""

import logging
from app.entities.chat_message import ChatMessage

logger = logging.getLogger("history")


class ConversationMemory:
    """
    Gestiona el historial de conversación para múltiples sesiones concurrentes.

    Los mensajes se almacenan en memoria usando session_id como clave. Los mensajes
    más antiguos se eliminan cuando la sesión supera el límite de _max_history entradas.
    """

    def __init__(self, max_history: int = 20) -> None:
        """
        Inicializa el almacenamiento de memoria de conversaciones.

        Args:
            max_history: Número máximo de mensajes retenidos por sesión.
        """
        self._sessions: dict[str, list[ChatMessage]] = {}
        self._max_history = max_history

    def add_message(self, session_id: str, message: ChatMessage) -> None:
        """
        Agrega un mensaje al historial de la sesión.

        Elimina el mensaje más antiguo cuando se supera el límite.

        Args:
            session_id: Identificador único de la sesión de conversación.
            message: ChatMessage a almacenar.
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append(message)
        if len(self._sessions[session_id]) > self._max_history:
            self._sessions[session_id].pop(0)
        logger.debug(
            "Message added to session %s (%d total).",
            session_id,
            len(self._sessions[session_id]),
        )

    def get_history(self, session_id: str) -> list[ChatMessage]:
        """
        Retorna el historial de conversación para la sesión indicada.

        Args:
            session_id: Identificador único de la sesión de conversación.

        Returns:
            Lista ordenada de objetos ChatMessage, o lista vacía si no existe.
        """
        return self._sessions.get(session_id, [])

    def clear_session(self, session_id: str) -> None:
        """
        Elimina todos los mensajes almacenados para la sesión indicada.

        Args:
            session_id: Identificador único de la sesión de conversación.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info("Session %s cleared.", session_id)

    def build_context_prompt(self, session_id: str) -> str:
        """
        Construye una transcripción formateada de la conversación para usar como contexto del LLM.

        Retorna una cadena alternando "Usuario: …\\nFlash: …" con los mensajes
        almacenados de la sesión.

        Args:
            session_id: Identificador único de la sesión de conversación.

        Returns:
            Cadena de conversación formateada, o cadena vacía para sesiones nuevas.
        """
        history = self.get_history(session_id)
        if not history:
            return ""
        lines: list[str] = []
        for msg in history:
            role_label = "Usuario" if msg.role == "user" else "Flash"
            lines.append(f"{role_label}: {msg.content}")
        return "\n".join(lines)
