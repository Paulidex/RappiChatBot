# app/analyzers/correlation_analyzer.py
"""Analizador de correlación: encuentra pares de métricas correlacionadas entre zonas."""

import logging
import statistics
from collections import defaultdict
from app.interfaces.i_insight_analyzer import IInsightAnalyzer
from app.entities.metric_record import MetricRecord
from app.entities.order_record import OrderRecord
from app.entities.insight_result import InsightResult

logger = logging.getLogger(__name__)


def _pearson(x: list[float], y: list[float]) -> float:
    """Calcula el coeficiente de correlación de Pearson para dos listas de igual longitud."""
    n = len(x)
    if n < 2:
        return 0.0
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)
    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    den_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
    den_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)


class CorrelationAnalyzer(IInsightAnalyzer):
    """
    Encuentra pares de métricas fuertemente correlacionadas entre zonas.

    Para cada zona, se usan los valores semanales (weekly_values) como series de tiempo. 
    Cualquier par de métricas con |correlación de Pearson| >= _min_correlation es reportado.
    """

    def __init__(self, min_correlation: float = 0.7) -> None:
        """
        Inicializa el analizador de correlación.

        Args:
            min_correlation: Valor mínimo absoluto de correlación de Pearson requerido
                para reportar un par.
        """
        self._min_correlation = min_correlation

    def _find_metric_correlations(
        self, metrics: list[MetricRecord]
    ) -> list[InsightResult]:
        """
        Organiza (pivot) las métricas por zona y calcula correlaciones de Pearson por pares.

        Args:
            metrics: Lista de objetos MetricRecord a analizar.

        Returns:
            Lista de objetos InsightResult para los pares correlacionados.
        """
        zone_metrics: dict[str, dict[str, list[float]]] = defaultdict(dict)
        for record in metrics:
            zone = record.zone_info.zone
            zone_metrics[zone][record.metric_name] = record.weekly_values

        results: list[InsightResult] = []
        reported_pairs: set[tuple] = set()

        for zone, metric_dict in zone_metrics.items():
            metric_names = list(metric_dict.keys())
            for i in range(len(metric_names)):
                for j in range(i + 1, len(metric_names)):
                    m1 = metric_names[i]
                    m2 = metric_names[j]
                    pair_key = tuple(sorted([m1, m2]))
                    if pair_key in reported_pairs:
                        continue
                    vals1 = metric_dict[m1]
                    vals2 = metric_dict[m2]
                    min_len = min(len(vals1), len(vals2))
                    if min_len < 3:
                        continue
                    try:
                        corr = _pearson(vals1[:min_len], vals2[:min_len])
                        if abs(corr) >= self._min_correlation:
                            reported_pairs.add(pair_key)
                            direction = "positiva" if corr > 0 else "negativa"
                            results.append(
                                InsightResult(
                                    category="correlation",
                                    severity="info",
                                    title=(
                                        f"Correlación {direction} entre "
                                        f"'{m1}' y '{m2}'"
                                    ),
                                    description=(
                                        f"Se detectó una correlación {direction} "
                                        f"de {corr:.2f} entre '{m1}' y '{m2}' "
                                        f"en la zona '{zone}'."
                                    ),
                                    recommendation=(
                                        f"Considerar la relación entre '{m1}' y "
                                        f"'{m2}' al planificar intervenciones en "
                                        f"'{zone}'."
                                    ),
                                    affected_zones=[zone],
                                    metadata={
                                        "metric_1": m1,
                                        "metric_2": m2,
                                        "correlation": round(corr, 4),
                                        "zone": zone,
                                    },
                                )
                            )
                    except Exception as exc:
                        logger.warning("Correlation calc failed: %s", exc)
        return results

    def analyze(
        self,
        metrics: list[MetricRecord],
        orders: list[OrderRecord],
    ) -> list[InsightResult]:
        """
        Analiza métricas para encontrar correlaciones fuertes entre pares.

        Args:
            metrics: Registros de métricas a analizar.
            orders: Registros de órdenes (no utilizados por este analizador).

        Returns:
            Lista de objetos InsightResult.
        """
        return self._find_metric_correlations(metrics)

    def get_category(self) -> str:
        """Devuelve el identificador de categoría para este analizador."""
        return "correlation"
