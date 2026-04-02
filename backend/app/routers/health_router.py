# app/routers/health_router.py
"""Router de verificación de estado (health-check) para la API de Rappi Insights."""

from fastapi import APIRouter


class HealthRouter:
    """
    Proporciona un endpoint simple de disponibilidad (liveness) para monitoreo
    y verificaciones de salud por balanceadores de carga.
    """

    def __init__(self) -> None:
        """Inicializa el router de health y registra la ruta GET /health."""
        self.router = APIRouter(tags=["Health"])
        self.router.add_api_route(
            "/health",
            self.get_health,
            methods=["GET"],
            status_code=200,
        )

    async def get_health(self) -> dict:
        """
        Retorna el estado actual de salud de la API.

        Returns:
            Diccionario con los campos status, version y bot_name.
        """
        return {
            "status": "healthy",
            "version": "1.0.0",
            "bot_name": "Flash",
        }
