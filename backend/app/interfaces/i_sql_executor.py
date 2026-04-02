# app/interfaces/i_sql_executor.py
"""Interfaz abstracta para la ejecución de SQL."""

from abc import ABC, abstractmethod


class ISqlExecutor(ABC):
    """
    Clase base abstracta para ejecutar consultas SQL contra una fuente de datos.

    Las implementaciones solo deben permitir sentencias SELECT.
    """

    @abstractmethod
    def execute(self, sql: str) -> list[dict]:
        """
        Ejecuta la consulta SQL proporcionada y retorna los resultados como una lista de diccionarios.

        Args:
            sql: Sentencia SQL SELECT a ejecutar.

        Returns:
            Lista de filas donde cada fila es un diccionario con claves como nombres de columnas.
        """
