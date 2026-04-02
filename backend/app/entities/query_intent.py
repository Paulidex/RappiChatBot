# app/entities/query_intent.py
"""Entidad de dominio QueryIntent."""

from dataclasses import dataclass, field


@dataclass
class QueryIntent:
    """
    Representa la intención clasificada de una consulta en lenguaje natural realizada por un usuario.

    Atributos:
        intent_type: Resultado de la clasificación ('chart', 'query' o 'general').
        original_question: El mensaje original del usuario.
        extracted_filters: Diccionario de filtros extraídos por el LLM
            (por ejemplo: país, métrica, zona).
    """

    intent_type: str
    original_question: str
    extracted_filters: dict = field(default_factory=dict)
