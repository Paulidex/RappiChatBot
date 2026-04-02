# app/analyzers/benchmark_analyzer.py
"""Analizador de referencia: compara zonas con promedios de zonas similares."""

import logging
import statistics
from collections import defaultdict
from app.interfaces.i_insight_analyzer import IInsightAnalyzer
from app.entities.metric_record import MetricRecord
from app.entities.order_record import OrderRecord
from app.entities.insight_result import InsightResult

logger = logging.getLogger(__name__)

DEVIATION_THRESHOLD = 1.5


class BenchmarkAnalyzer(IInsightAnalyzer):
    """
    Identifica zonas que tienen un desempeño significativamente inferior frente a su grupo comparable.

    Las zonas se agrupan por (país, tipo de zona, nombre de la métrica). 
    Cualquier zona cuyo valor actual esté más de DEVIATION_THRESHOLD desviaciones estándar por debajo del promedio del grupo es marcada.
    """

    def _compare_similar_zones(
        self, metrics: list[MetricRecord]
    ) -> list[InsightResult]:
        """
        Agrupa métricas por atributos comparables y marca los casos con bajo rendimiento estadístico.

        Args:
            metrics: Lista de objetos MetricRecord para comparar.

        Returns:
            Lista de objetos InsightResult para las zonas con bajo rendimiento.
        """
        groups: dict[tuple, list[MetricRecord]] = defaultdict(list)
        for record in metrics:
            key = (
                record.zone_info.country,
                record.zone_info.zone_type,
                record.metric_name,
            )
            groups[key].append(record)

        results: list[InsightResult] = []
        for (country, zone_type, metric_name), group in groups.items():
            if len(group) < 3:
                continue
            try:
                current_values = [r.get_current_value() for r in group]
                mean = statistics.mean(current_values)
                stdev = statistics.stdev(current_values)
                if stdev == 0:
                    continue
                for record in group:
                    val = record.get_current_value()
                    z_score = (val - mean) / stdev
                    if z_score < -DEVIATION_THRESHOLD:
                        results.append(
                            InsightResult(
                                category="benchmark",
                                severity="warning",
                                title=(
                                    f"Bajo rendimiento en benchmarking — "
                                    f"{record.zone_info.zone}"
                                ),
                                description=(
                                    f"La zona '{record.zone_info.zone}' tiene "
                                    f"'{metric_name}' = {val:.2f}, que es "
                                    f"{abs(z_score):.1f} desviaciones estándar por "
                                    f"debajo del promedio ({mean:.2f}) de zonas "
                                    f"similares ({zone_type}) en {country}."
                                ),
                                recommendation=(
                                    f"Investigar por qué '{record.zone_info.zone}' "
                                    f"está rezagada en '{metric_name}' vs. pares "
                                    f"de tipo '{zone_type}' en {country}."
                                ),
                                affected_zones=[record.zone_info.zone],
                                metadata={
                                    "metric": metric_name,
                                    "country": country,
                                    "zone_type": zone_type,
                                    "zone_value": round(val, 4),
                                    "group_mean": round(mean, 4),
                                    "group_stdev": round(stdev, 4),
                                    "z_score": round(z_score, 4),
                                },
                            )
                        )
            except Exception as exc:
                logger.warning("Benchmark comparison failed: %s", exc)
        return results

    def analyze(
        self,
        metrics: list[MetricRecord],
        orders: list[OrderRecord],
    ) -> list[InsightResult]:
        """
        Analiza métricas para identificar bajo rendimiento mediante benchmarking.

        Args:
            metrics: Registros de métricas a analizar.
            orders: Registros de órdenes (no utilizados por este analizador).

        Returns:
            Lista de objetos InsightResult.
        """
        return self._compare_similar_zones(metrics)

    def get_category(self) -> str:
        """Devuelve el identificador de categoría para este analizador."""
        return "benchmark"
