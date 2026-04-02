# app/routers/insight_router.py
"""Router de FastAPI para los endpoints de insights automatizados de Flash."""

import base64
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.interfaces.i_insight_service import IInsightService
from app.models.requests import ReportPdfRequest
from app.models.responses import InitialInsightsResponse

logger = logging.getLogger(__name__)

AVAILABLE_CATEGORIES = ["anomaly", "trend", "benchmark", "correlation"]


class InsightRouter:
    """
    Expone los endpoints de insights automatizados de Flash bajo /insights.

    Endpoints:
        GET  /insights/initial      — retornar 10 insights precomputados
        POST /insights/report-pdf   — generar reporte ejecutivo en PDF
        GET  /insights/categories   — listar categorías de insights disponibles
    """

    def __init__(self, insight_service: IInsightService) -> None:
        """
        Inicializa el router de insights con su dependencia de servicio.

        Args:
            insight_service: Implementación de IInsightService.
        """
        self._insight_service = insight_service
        self.router = APIRouter(tags=["Insights"])
        self._register_routes()

    def _register_routes(self) -> None:
        """Registra todos los manejadores de rutas en self.router."""
        self.router.add_api_route(
            "/insights/initial",
            self.get_initial_insights,
            methods=["GET"],
            response_model=InitialInsightsResponse,
            status_code=200,
        )
        self.router.add_api_route(
            "/insights/report-pdf",
            self.generate_report_pdf,
            methods=["POST"],
            status_code=200,
        )
        self.router.add_api_route(
            "/insights/categories",
            self.get_available_categories,
            methods=["GET"],
            status_code=200,
        )

    async def get_initial_insights(self) -> InitialInsightsResponse:
        """
        Ejecuta las 10 consultas predefinidas y retorna datos de insights + gráficos.

        Returns:
            InitialInsightsResponse con insights_data y chart_base64_list.

        Raises:
            HTTPException 500: En errores inesperados de procesamiento.
        """
        try:
            return self._insight_service.generate_initial_insights()
        except Exception as exc:
            logger.error("GET /insights/initial error: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))

    async def generate_report_pdf(self, request: ReportPdfRequest) -> Response:
        """
        Genera un reporte ejecutivo en PDF y lo devuelve como archivo descargable.

        Args:
            request: ReportPdfRequest con insights y rutas de gráficos opcionales.

        Returns:
            Respuesta HTTP con el PDF como archivo inline.

        Raises:
            HTTPException 400: Si la solicitud es inválida.
            HTTPException 500: En errores inesperados de procesamiento.
        """
        try:
            pdf_response = self._insight_service.generate_report_pdf(request)
            pdf_bytes = base64.b64decode(pdf_response.pdf_base64)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f"inline; filename={pdf_response.filename}"},
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except Exception as exc:
            logger.error("POST /insights/report-pdf error: %s", exc)
            raise HTTPException(status_code=500, detail=str(exc))

    async def get_available_categories(self) -> dict:
        """
        Retorna la lista de categorías de insights disponibles.

        Returns:
            Diccionario con la clave 'categories' que lista las cuatro categorías de analizadores.
        """
        return {"categories": AVAILABLE_CATEGORIES}
