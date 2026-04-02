# app/entities/order_record.py
"""Entidad de dominio OrderRecord."""

from dataclasses import dataclass, field
from app.entities.zone_info import ZoneInfo


@dataclass
class OrderRecord:
    """
    Representa el volumen semanal de pedidos para una zona específica.

    weekly_orders contiene 9 entradas ordenadas de la más antigua a la más reciente:
    [L8W, L7W, L6W, L5W, L4W, L3W, L2W, L1W, L0W].

    Atributos:
        zone_info: Información geográfica y de clasificación de la zona.
        weekly_orders: Lista de 9 cantidades de pedidos semanales (de más antiguo → más reciente).
    """

    zone_info: ZoneInfo
    weekly_orders: list[float] = field(default_factory=list)

    def get_current_orders(self) -> float:
        """Retorna la cantidad de pedidos de la semana más reciente (L0W)."""
        return self.weekly_orders[-1] if self.weekly_orders else 0.0

    def get_growth_rate(self) -> float:
        """
        Calcula la tasa de crecimiento semana a semana (WoW) de los pedidos.

        Returns:
            Float que representa el crecimiento relativo. Retorna 0.0 si la
            semana anterior tiene cero pedidos.
        """
        if len(self.weekly_orders) < 2:
            return 0.0
        previous = self.weekly_orders[-2]
        if previous == 0:
            return 0.0
        return (self.get_current_orders() - previous) / previous
