# app/interfaces/i_metric_repository.py
"""Interfaz abstracta para el repositorio de métricas."""

from abc import ABC, abstractmethod
from app.entities.metric_record import MetricRecord


class IMetricRepository(ABC):
    """
    Clase base abstracta que define el contrato para el acceso a datos de métricas.

    Las implementaciones deben proporcionar métodos para consultar objetos MetricRecord
    desde la fuente de datos subyacente.
    """

    @abstractmethod
    def get_all(self) -> list[MetricRecord]:
        """Retorna todos los registros de métricas."""

    @abstractmethod
    def get_by_country(self, country: str) -> list[MetricRecord]:
        """
        Retorna registros de métricas filtrados por código de país.

        Args:
            country: Código de país de dos letras.
        """

    @abstractmethod
    def get_by_zone(self, zone: str) -> list[MetricRecord]:
        """
        Retorna registros de métricas para una zona específica.

        Args:
            zone: Nombre de la zona.
        """

    @abstractmethod
    def get_by_metric_name(self, metric: str) -> list[MetricRecord]:
        """
        Retorna registros de una métrica específica en todas las zonas.

        Args:
            metric: Nombre de la métrica.
        """

    @abstractmethod
    def filter_metrics(
        self,
        country: str = "",
        city: str = "",
        zone: str = "",
        metric: str = "",
    ) -> list[MetricRecord]:
        """
        Retorna registros que coinciden con todos los criterios de filtro proporcionados (no vacíos).

        Args:
            country: Filtro opcional por país.
            city: Filtro opcional por ciudad.
            zone: Filtro opcional por zona.
            metric: Filtro opcional por nombre de la métrica.
        """
