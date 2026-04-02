# app/analyzers/trend_analyzer.py
"""Analizador de tendencias: detecta caídas consecutivas semanales en métricas."""

import logging
from app.interfaces.i_insight_analyzer import IInsightAnalyzer
from app.entities.metric_record import MetricRecord
from app.entities.order_record import OrderRecord
from app.entities.insight_result import InsightResult

logger = logging.getLogger(__name__)


class TrendAnalyzer(IInsightAnalyzer):
    """
    Detecta métricas que han disminuido durante N o más semanas consecutivas.

    Se marca una tendencia decreciente cuando weekly_values disminuye durante al menos
    _min_consecutive_weeks períodos seguidos
    """

    def __init__(self, min_consecutive_weeks: int = 3) -> None:
        """
        Inicializa el analizador de tendencias.

        Args:
            min_consecutive_weeks: Número mínimo de semanas consecutivas de caída
                requeridas para marcar una tendencia.
        """
        self._min_consecutive_weeks = min_consecutive_weeks

    def _find_declining_trends(
        self, metrics: list[MetricRecord]
    ) -> list[InsightResult]:
        """
        Recorre los valores semanales en busca de períodos consecutivos de disminución.

        Args:
            metrics: Lista de objetos MetricRecord a inspeccionar.

        Returns:
            Lista de objetos InsightResult por cada tendencia decreciente detectada.
        """
        results: list[InsightResult] = []
        for record in metrics:
            try:
                values = record.weekly_values
                if len(values) < self._min_consecutive_weeks + 1:
                    continue
                max_streak = 0
                current_streak = 0
                for i in range(1, len(values)):
                    if values[i] < values[i - 1]:
                        current_streak += 1
                        max_streak = max(max_streak, current_streak)
                    else:
                        current_streak = 0
                if max_streak >= self._min_consecutive_weeks:
                    total_change = (
                        (values[-1] - values[0]) / values[0] * 100
                        if values[0] != 0
                        else 0.0
                    )
                    results.append(
                        InsightResult(
                            category="trend",
                            severity="warning",
                            title=(
                                f"Tendencia decreciente en {record.metric_name} — "
                                f"{record.zone_info.zone}"
                            ),
                            description=(
                                f"La métrica '{record.metric_name}' en "
                                f"'{record.zone_info.zone}' "
                                f"({record.zone_info.country}) ha mostrado "
                                f"{max_streak} semanas consecutivas de declive. "
                                f"Cambio acumulado: {total_change:.1f}%."
                            ),
                            recommendation=(
                                f"Revisar operaciones en '{record.zone_info.zone}' "
                                f"para identificar causas del deterioro continuo "
                                f"en '{record.metric_name}'."
                            ),
                            affected_zones=[record.zone_info.zone],
                            metadata={
                                "metric": record.metric_name,
                                "country": record.zone_info.country,
                                "consecutive_weeks": max_streak,
                                "total_change_pct": round(total_change, 2),
                                "weekly_values": values,
                            },
                        )
                    )
            except Exception as exc:
                logger.warning("Trend check failed for record: %s", exc)
        return results

    def analyze(
        self,
        metrics: list[MetricRecord],
        orders: list[OrderRecord],
    ) -> list[InsightResult]:
        """
        Analiza métricas para detectar tendencias decrecientes consecutivas.

        Args:
            metrics: Registros de métricas a analizar.
            orders: Registros de órdenes (no utilizados por este analizador).

        Returns:
            Lista de objetos InsightResult.
        """
        return self._find_declining_trends(metrics)

    def get_category(self) -> str:
        """Devuelve el identificador de categoría para este analizador."""
        return "trend"
