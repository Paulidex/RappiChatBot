# app/interfaces/i_order_repository.py
"""Interfaz abstracta para el repositorio de órdenes."""

from abc import ABC, abstractmethod
from app.entities.order_record import OrderRecord


class IOrderRepository(ABC):
    """
    Clase base abstracta que define el contrato para el acceso a datos de órdenes.

    Las implementaciones deben proporcionar métodos para consultar objetos OrderRecord
    desde la fuente de datos subyacente.
    """

    @abstractmethod
    def get_all(self) -> list[OrderRecord]:
        """Retorna todos los registros de órdenes."""

    @abstractmethod
    def get_by_country(self, country: str) -> list[OrderRecord]:
        """
        Retorna registros de órdenes filtrados por código de país.

        Args:
            country: Código de país de dos letras.
        """

    @abstractmethod
    def get_by_zone(self, zone: str) -> list[OrderRecord]:
        """
        Retorna registros de órdenes para una zona específica.

        Args:
            zone: Nombre de la zona.
        """

    @abstractmethod
    def get_top_growing_zones(self, n: int, weeks: int) -> list[OrderRecord]:
        """
        Retorna las N zonas principales ordenadas por crecimiento de órdenes en las últimas N semanas.

        Args:
            n: Número de zonas principales a retornar.
            weeks: Número de semanas recientes a considerar para el cálculo del crecimiento.
        """
