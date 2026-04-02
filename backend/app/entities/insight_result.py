# app/entities/insight_result.py
"""Entidad de dominio InsightResult."""

from dataclasses import dataclass, field


@dataclass
class InsightResult:
    """
    Representa un insight de negocio accionable detectado por un analizador.

    Atributos:
        category: Categoría del insight ('anomaly', 'trend', 'benchmark',
            'correlation').
        severity: Nivel de severidad ('critical', 'warning', 'info').
        title: Título corto y legible para el insight.
        description: Explicación detallada de lo que se encontró.
        recommendation: Recomendación accionable para el negocio.
        affected_zones: Lista de identificadores de zonas afectadas por este insight.
        metadata: Datos adicionales arbitrarios provenientes del analizador.
    """

    category: str
    severity: str
    title: str
    description: str
    recommendation: str
    affected_zones: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
