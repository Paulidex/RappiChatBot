# app/interfaces/i_chart_generator.py
"""Interfaz abstracta para la generación de gráficos."""

from abc import ABC, abstractmethod


class IChartGenerator(ABC):
    """
    Clase base abstracta para generar visualizaciones de datos.

    Las implementaciones producen gráficos codificados como cadenas base64 para que puedan
    ser incrustados directamente en las respuestas de la API.
    """

    @abstractmethod
    def generate_chart(self, question: str, data: list[dict]) -> str:
        """
        Genera un gráfico a partir de los datos proporcionados y lo codifica en base64.

        Args:
            question: Pregunta del usuario, usada para inferir el tipo de gráfico y el título.
            data: Filas de datos a visualizar.

        Returns:
            Cadena de imagen PNG codificada en base64.
        """
