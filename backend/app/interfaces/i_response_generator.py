# app/interfaces/i_response_generator.py
"""Interfaz abstracta para la generación de respuestas en lenguaje natural."""

from abc import ABC, abstractmethod


class IResponseGenerator(ABC):
    """
    Clase base abstracta para generar respuestas en lenguaje natural.

    Las implementaciones utilizan un LLM para interpretar datos o responder preguntas
    en español conversacional.
    """

    @abstractmethod
    def generate(self, question: str, data: list[dict]) -> str:
        """
        Genera una respuesta en lenguaje natural para la pregunta y los datos proporcionados.

        Args:
            question: Pregunta original del usuario (puede incluir contexto
                del historial para intenciones generales).
            data: Resultados de la consulta a interpretar. Una lista vacía
                activa una respuesta conversacional/general.

        Returns:
            Cadena de texto legible para humanos en español.
        """
