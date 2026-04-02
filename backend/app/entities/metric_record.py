# app/entities/metric_record.py
"""Entidad de dominio MetricRecord."""

from dataclasses import dataclass, field
from app.entities.zone_info import ZoneInfo


@dataclass
class MetricRecord:
    """
    Representa una métrica acumulada semanal para una zona específica.

    weekly_values contiene 9 entradas ordenadas de la más antigua a la más reciente:
    [L8W_ROLL, L7W_ROLL, L6W_ROLL, L5W_ROLL, L4W_ROLL, L3W_ROLL, L2W_ROLL,
    L1W_ROLL, L0W_ROLL].

    Atributos:
        zone_info: Información geográfica y de clasificación de la zona.
        metric_name: Nombre de la métrica operativa.
        weekly_values: Lista de 9 valores semanales acumulados (de más antiguo → más reciente).
    """

    zone_info: ZoneInfo
    metric_name: str
    weekly_values: list[float] = field(default_factory=list)

    def get_current_value(self) -> float:
        """Retorna el valor más reciente (L0W_ROLL)."""
        return self.weekly_values[-1] if self.weekly_values else 0.0

    def get_previous_value(self) -> float:
        """Retorna el valor de la semana anterior (L1W_ROLL)."""
        return self.weekly_values[-2] if len(self.weekly_values) >= 2 else 0.0

    def get_wow_change(self) -> float:
        """
        Calcula el cambio porcentual semana a semana (WoW).

        Returns:
            Float que representa el cambio relativo. Retorna 0.0 si el valor
            anterior es cero para evitar división por cero.
        """
        previous = self.get_previous_value()
        if previous == 0:
            return 0.0
        return (self.get_current_value() - previous) / previous
