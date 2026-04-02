# app/analyzers/anomaly_analyzer.py
"""Analizador de detección de anomalías para cambios métricos semana a semana."""

import logging
from app.interfaces.i_insight_analyzer import IInsightAnalyzer
from app.entities.metric_record import MetricRecord
from app.entities.order_record import OrderRecord
from app.entities.insight_result import InsightResult

logger = logging.getLogger(__name__)

CRITICAL_THRESHOLD = 0.20
WARNING_THRESHOLD = 0.10


class AnomalyAnalyzer(IInsightAnalyzer):
    """
    Detecta anomalías semana a semana (WoW) en métricas operativas.

    Se marca una anomalía 'crítica' cuando |cambio WoW| > 20%.
    Se marca una anomalía de 'advertencia' cuando |cambio WoW| > umbral (por defecto 10%).
    """

    def __init__(self, threshold: float = 0.10) -> None:
        """
        Inicializa el analizador de anomalías.

        Args:
            threshold: Cambio absoluto mínimo WoW para marcar como advertencia.
        """
        self._threshold = threshold

    def _detect_wow_anomalies(
        self, metrics: list[MetricRecord]
    ) -> list[InsightResult]:
        """
        Itera sobre los registros de métricas y marca aquellos con grandes cambios WoW.

        Args:
            metrics: Lista de objetos MetricRecord a inspeccionar.

        Returns:
            Lista de objetos InsightResult por cada anomalía detectada.
        """
        results: list[InsightResult] = []
        for record in metrics:
            try:
                change = record.get_wow_change()
                abs_change = abs(change)
                if abs_change <= self._threshold:
                    continue
                severity = "critical" if abs_change > CRITICAL_THRESHOLD else "warning"
                direction = "aumentó" if change > 0 else "disminuyó"
                results.append(
                    InsightResult(
                        category="anomaly",
                        severity=severity,
                        title=(
                            f"Anomalía en {record.metric_name} — "
                            f"{record.zone_info.zone}"
                        ),
                        description=(
                            f"La métrica '{record.metric_name}' en la zona "
                            f"'{record.zone_info.zone}' ({record.zone_info.country}) "
                            f"{direction} un {abs_change * 100:.1f}% semana a semana."
                        ),
                        recommendation=(
                            f"Investigar las causas del cambio en "
                            f"'{record.metric_name}' para la zona "
                            f"'{record.zone_info.zone}'."
                        ),
                        affected_zones=[record.zone_info.zone],
                        metadata={
                            "metric": record.metric_name,
                            "country": record.zone_info.country,
                            "wow_change": round(change, 4),
                            "current_value": record.get_current_value(),
                            "previous_value": record.get_previous_value(),
                        },
                    )
                )
            except Exception as exc:
                logger.warning("Anomaly check failed for record: %s", exc)
        return results

    def analyze(
        self,
        metrics: list[MetricRecord],
        orders: list[OrderRecord],
    ) -> list[InsightResult]:
        """
        Analiza métricas para detectar anomalías semana a semana (WoW).

        Args:
            metrics: Registros de métricas a analizar.
            orders: Registros de órdenes (no utilizados por este analizador).

        Returns:
            Lista de objetos InsightResult.
        """
        return self._detect_wow_anomalies(metrics)

    def get_category(self) -> str:
        """Devuelve el identificador de categoría para este analizador."""
        return "anomaly"
