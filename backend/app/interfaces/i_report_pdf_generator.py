# app/interfaces/i_report_pdf_generator.py
"""Interfaz abstracta para la generación de reportes PDF."""

from abc import ABC, abstractmethod
from app.entities.insight_result import InsightResult


class IReportPdfGenerator(ABC):
    """
    Clase base abstracta para generar reportes ejecutivos en PDF.

    Las implementaciones utilizan un LLM para redactar contenido narrativo y luego
    lo combinan con gráficos para renderizar un documento PDF.
    """

    @abstractmethod
    def generate_pdf(
        self,
        insights: list[InsightResult],
        charts: list[str],
        title: str,
    ) -> bytes:
        """
        Genera un reporte en PDF a partir de datos de insights y gráficos.

        Args:
            insights: Lista de objetos InsightResult a incluir.
            charts: Lista de imágenes de gráficos codificadas en base64.
            title: Título del reporte.

        Returns:
            Contenido del archivo PDF como bytes en bruto.
        """
