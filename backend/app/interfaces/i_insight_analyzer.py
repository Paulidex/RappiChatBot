# app/interfaces/i_insight_analyzer.py
"""Interfaz abstracta para analizadores de insights (patrón Strategy)."""

from abc import ABC, abstractmethod
from app.entities.metric_record import MetricRecord
from app.entities.order_record import OrderRecord
from app.entities.insight_result import InsightResult


class IInsightAnalyzer(ABC):
    """
    Clase base abstracta para las estrategias de análisis de insights.

    Cada implementación concreta maneja un tipo de análisis
    (anomaly, trend, benchmark, correlation) siguiendo el patrón Strategy.
    """

    @abstractmethod
    def analyze(
        self,
        metrics: list[MetricRecord],
        orders: list[OrderRecord],
    ) -> list[InsightResult]:
        """
        Analiza los datos proporcionados y retorna los insights detectados.

        Args:
            metrics: Lista de registros de métricas a analizar.
            orders: Lista de registros de órdenes a analizar.

        Returns:
            Lista de objetos InsightResult que describen los hallazgos.
        """

    @abstractmethod
    def get_category(self) -> str:
        """Retorna la cadena de categoría que maneja este analizador."""
