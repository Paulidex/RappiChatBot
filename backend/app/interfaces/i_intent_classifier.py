# app/interfaces/i_intent_classifier.py
"""Interfaz abstracta para la clasificación de intención."""

from abc import ABC, abstractmethod
from app.entities.query_intent import QueryIntent


class IIntentClassifier(ABC):
    """
    Clase base abstracta para clasificar la intención de los mensajes del usuario.

    Las implementaciones determinan si un mensaje debe generar un gráfico,
    una consulta de datos o una respuesta conversacional general.
    """

    @abstractmethod
    def classify(self, user_message: str) -> QueryIntent:
        """
        Clasifica la intención de un mensaje del usuario.

        Args:
            user_message: Texto en bruto proveniente del usuario.

        Returns:
            QueryIntent con intent_type y filtros extraídos.
        """
