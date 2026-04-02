# app/interfaces/i_insight_service.py
"""Interfaz abstracta para el servicio de insights."""

from abc import ABC, abstractmethod
from app.models.requests import ReportPdfRequest
from app.models.responses import InitialInsightsResponse, ReportPdfResponse


class IInsightService(ABC):
    """
    Clase base abstracta para el servicio de generación de insights.

    Orquesta la ejecución de consultas analíticas predefinidas, la generación
    de gráficos y la producción de reportes en PDF.
    """

    @abstractmethod
    def generate_initial_insights(self) -> InitialInsightsResponse:
        """
        Ejecuta las 10 consultas de insights predefinidas y retorna los resultados.

        Returns:
            InitialInsightsResponse con filas de datos y gráficos en base64.
        """

    @abstractmethod
    def generate_report_pdf(self, request: ReportPdfRequest) -> ReportPdfResponse:
        """
        Genera un reporte ejecutivo en PDF a partir de los datos de insights proporcionados.

        Args:
            request: ReportPdfRequest que contiene los insights y las rutas de los gráficos.

        Returns:
            ReportPdfResponse con el PDF codificado en base64.
        """
