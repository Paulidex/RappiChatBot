# app/interfaces/i_sql_generator.py
"""Interfaz abstracta para la generación de SQL."""

from abc import ABC, abstractmethod
from app.entities.query_intent import QueryIntent


class ISqlGenerator(ABC):
    """
    Clase base abstracta para generar SQL a partir de una intención de usuario clasificada.

    Las implementaciones traducen intenciones en lenguaje natural en sentencias
    SELECT válidas de SQLite.
    """

    @abstractmethod
    def generate_sql(self, intent: QueryIntent) -> str:
        """
        Genera una sentencia SQL SELECT a partir de la intención dada.

        Args:
            intent: Intención de consulta clasificada con filtros extraídos.

        Returns:
            Sentencia SELECT válida de SQLite como cadena.
        """
