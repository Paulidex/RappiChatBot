# app/entities/chat_message.py
"""Entidad de dominio ChatMessage."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ChatMessage:
    """
    Representa un único mensaje en una conversación con Flash.

    Atributos:
        role: Quién envió el mensaje ('user' o 'assistant').
        content: El contenido textual del mensaje.
        timestamp: Marca de tiempo en formato ISO (UTC) de cuándo se creó el mensaje.
        message_type: Tipo de contenido del mensaje ('text', 'chart' o 'error').
    """

    role: str
    content: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    message_type: str = "text"
