# app/entities/zone_info.py
"""Entidad de dominio ZoneInfo."""

from dataclasses import dataclass


@dataclass
class ZoneInfo:
    """
    Representa información geográfica y de clasificación para una zona de Rappi.

    Atributos:
        country: Código de país de dos letras (por ejemplo: 'CO', 'MX').
        city: Nombre de la ciudad.
        zone: Nombre de la zona.
        zone_type: Clasificación de la zona ('Wealthy' o 'Non Wealthy').
        zone_prioritization: Nivel de prioridad ('High Priority', 'Prioritized',
            o 'Not Prioritized').
    """

    country: str
    city: str
    zone: str
    zone_type: str
    zone_prioritization: str
