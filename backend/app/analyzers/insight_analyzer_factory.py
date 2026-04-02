# app/analyzers/insight_analyzer_factory.py
"""Fábrica para crear instancias de IInsightAnalyzer."""

import logging
from app.interfaces.i_insight_analyzer import IInsightAnalyzer
from app.analyzers.anomaly_analyzer import AnomalyAnalyzer
from app.analyzers.trend_analyzer import TrendAnalyzer
from app.analyzers.benchmark_analyzer import BenchmarkAnalyzer
from app.analyzers.correlation_analyzer import CorrelationAnalyzer
from app.config.settings import Settings

logger = logging.getLogger(__name__)

_CATEGORY_MAP: dict[str, type] = {
    "anomaly": AnomalyAnalyzer,
    "trend": TrendAnalyzer,
    "benchmark": BenchmarkAnalyzer,
    "correlation": CorrelationAnalyzer,
}


class InsightAnalyzerFactory:
    """
    Fábrica que crea instancias de IInsightAnalyzer utilizando la configuración de la aplicación.

    Proporciona métodos para instanciar todos los analizadores a la vez o un solo
    analizador según el nombre de la categoría.
    """

    @classmethod
    def create_all_analyzers(cls) -> list[IInsightAnalyzer]:
        """
        Crea y retorna los cuatro analizadores de insights configurados mediante Settings.

        Returns:
            Lista que contiene AnomalyAnalyzer, TrendAnalyzer,
            BenchmarkAnalyzer y CorrelationAnalyzer.
        """
        settings = Settings.get_instance()
        return [
            AnomalyAnalyzer(threshold=settings.anomaly_threshold),
            TrendAnalyzer(min_consecutive_weeks=settings.trend_min_weeks),
            BenchmarkAnalyzer(),
            CorrelationAnalyzer(),
        ]

    @classmethod
    def create_analyzer(cls, category: str) -> IInsightAnalyzer:
        """
        Crea y retorna un solo analizador según el nombre de la categoría.

        Args:
            category: Uno de 'anomaly', 'trend', 'benchmark', 'correlation'.

        Returns:
            Implementación de IInsightAnalyzer configurada.

        Raises:
            ValueError: Si la categoría no es reconocida.
        """
        settings = Settings.get_instance()
        if category not in _CATEGORY_MAP:
            raise ValueError(
                f"Unknown analyzer category '{category}'. "
                f"Valid options: {list(_CATEGORY_MAP.keys())}"
            )
        if category == "anomaly":
            return AnomalyAnalyzer(threshold=settings.anomaly_threshold)
        if category == "trend":
            return TrendAnalyzer(min_consecutive_weeks=settings.trend_min_weeks)
        return _CATEGORY_MAP[category]()
