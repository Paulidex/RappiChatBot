# app/services/insight_service.py
"""InsightService — orquesta la generación automatizada de insights para Flash."""

import base64
import logging
from datetime import datetime
from app.interfaces.i_insight_service import IInsightService
from app.interfaces.i_metric_repository import IMetricRepository
from app.interfaces.i_order_repository import IOrderRepository
from app.interfaces.i_response_generator import IResponseGenerator
from app.interfaces.i_chart_generator import IChartGenerator
from app.interfaces.i_report_pdf_generator import IReportPdfGenerator
from app.interfaces.i_insight_analyzer import IInsightAnalyzer
from app.entities.insight_result import InsightResult
from app.models.requests import ReportPdfRequest
from app.models.responses import InitialInsightsResponse, ReportPdfResponse
from app.config.settings import Settings
from app.database.sqlite_executor import SqliteExecutor

logger = logging.getLogger("insight")


class InsightService(IInsightService):
    """
    Ejecuta consultas SQL de insights predefinidas, genera gráficos y
    produce reportes ejecutivos en PDF.

    Las 10 INITIAL_QUERIES se ejecutan cuando el frontend lo solicita para
    llenar el dashboard de insights. Cuando el usuario presiona 'Generate
    Report', se llama a generate_report_pdf para crear el PDF.
    """

    INITIAL_QUERIES: list[dict] = [
        {
            "chart_type": "horizontal_bar",
            "title": "Top ciudades por Lead Penetration esta semana",
            "sql": (
                "SELECT CITY, AVG(L0W_ROLL) as valor_actual FROM metrics "
                "WHERE METRIC = 'Lead Penetration' "
                "GROUP BY CITY ORDER BY valor_actual DESC LIMIT 10"
            ),
        },
        {
            "chart_type": "horizontal_bar",
            "title": "Variación semanal (WoW) de Perfect Orders por zona",
            "sql": (
                "SELECT ZONE, COUNTRY, L0W_ROLL, L1W_ROLL, "
                "ROUND(L0W_ROLL - L1W_ROLL, 4) as variacion_wow "
                "FROM metrics WHERE METRIC = 'Perfect Orders' "
                "AND L1W_ROLL IS NOT NULL "
                "ORDER BY variacion_wow DESC LIMIT 10"
            ),
        },
        {
            "chart_type": "line",
            "title": "Tendencia 8 semanas de órdenes por país",
            "sql": (
                "SELECT COUNTRY, "
                "SUM(L8W) as L8W, SUM(L7W) as L7W, SUM(L6W) as L6W, "
                "SUM(L5W) as L5W, SUM(L4W) as L4W, SUM(L3W) as L3W, "
                "SUM(L2W) as L2W, SUM(L1W) as L1W, SUM(L0W) as L0W "
                "FROM orders GROUP BY COUNTRY"
            ),
        },
        {
            "chart_type": "bar",
            "title": "Promedio histórico vs valor actual — Gross Profit UE por país",
            "sql": (
                "SELECT COUNTRY, "
                "ROUND(AVG(L0W_ROLL), 4) as valor_actual, "
                "ROUND((L8W_ROLL+L7W_ROLL+L6W_ROLL+L5W_ROLL+L4W_ROLL+"
                "L3W_ROLL+L2W_ROLL+L1W_ROLL+L0W_ROLL)/9.0, 4) as promedio_historico "
                "FROM metrics WHERE METRIC = 'Gross Profit UE' "
                "GROUP BY COUNTRY ORDER BY valor_actual DESC"
            ),
        },
        {
            "chart_type": "horizontal_bar",
            "title": "Desviación vs promedio histórico — Pro Adoption por zona",
            "sql": (
                "SELECT ZONE, COUNTRY, "
                "ROUND(L0W_ROLL - (L8W_ROLL+L7W_ROLL+L6W_ROLL+L5W_ROLL+L4W_ROLL+"
                "L3W_ROLL+L2W_ROLL+L1W_ROLL+L0W_ROLL)/9.0, 4) as desviacion "
                "FROM metrics WHERE METRIC = 'Pro Adoption (Last Week Status)' "
                "ORDER BY desviacion DESC LIMIT 10"
            ),
        },
        {
            "chart_type": "horizontal_bar",
            "title": "Top ciudades por Turbo Adoption",
            "sql": (
                "SELECT CITY, ROUND(AVG(L0W_ROLL), 4) as valor FROM metrics "
                "WHERE METRIC = 'Turbo Adoption' "
                "GROUP BY CITY ORDER BY valor DESC LIMIT 10"
            ),
        },
        {
            "chart_type": "pie",
            "title": "Comparación Wealthy vs Non Wealthy — Perfect Orders",
            "sql": (
                "SELECT ZONE_TYPE, ROUND(AVG(L0W_ROLL), 4) as promedio FROM metrics "
                "WHERE METRIC = 'Perfect Orders' GROUP BY ZONE_TYPE"
            ),
        },
        {
            "chart_type": "line",
            "title": "Evolución 8 semanas por priorización de zona — Lead Penetration",
            "sql": (
                "SELECT ZONE_PRIORITIZATION, "
                "ROUND(AVG(L8W_ROLL),4) as L8W, ROUND(AVG(L7W_ROLL),4) as L7W, "
                "ROUND(AVG(L6W_ROLL),4) as L6W, ROUND(AVG(L5W_ROLL),4) as L5W, "
                "ROUND(AVG(L4W_ROLL),4) as L4W, ROUND(AVG(L3W_ROLL),4) as L3W, "
                "ROUND(AVG(L2W_ROLL),4) as L2W, ROUND(AVG(L1W_ROLL),4) as L1W, "
                "ROUND(AVG(L0W_ROLL),4) as L0W "
                "FROM metrics WHERE METRIC = 'Lead Penetration' "
                "GROUP BY ZONE_PRIORITIZATION"
            ),
        },
        {
            "chart_type": "horizontal_bar",
            "title": "Zonas con caídas fuertes esta semana (anomalías WoW)",
            "sql": (
                "SELECT ZONE, COUNTRY, METRIC, "
                "ROUND(L0W_ROLL - L1W_ROLL, 4) as caida "
                "FROM metrics "
                "WHERE L1W_ROLL IS NOT NULL AND L1W_ROLL > 0 "
                "AND (L0W_ROLL - L1W_ROLL) / L1W_ROLL < -0.15 "
                "ORDER BY caida ASC LIMIT 10"
            ),
        },
        {
            "chart_type": "horizontal_bar",
            "title": "Velocidad de cambio 8 semanas — Restaurants SS > ATC CVR",
            "sql": (
                "SELECT ZONE, COUNTRY, "
                "ROUND((L0W_ROLL - L8W_ROLL) / 8.0, 5) as velocidad_cambio "
                "FROM metrics WHERE METRIC = 'Restaurants SS > ATC CVR' "
                "AND L8W_ROLL IS NOT NULL "
                "ORDER BY ABS(velocidad_cambio) DESC LIMIT 10"
            ),
        },
    ]

    def __init__(
        self,
        metric_repo: IMetricRepository,
        order_repo: IOrderRepository,
        response_generator: IResponseGenerator,
        chart_generator: IChartGenerator,
        report_pdf_gen: IReportPdfGenerator,
        analyzers: list[IInsightAnalyzer],
    ) -> None:
        """
        Inicializa InsightService con sus colaboradores.

        Args:
            metric_repo: Repositorio de datos de métricas.
            order_repo: Repositorio de datos de órdenes.
            response_generator: Genera resúmenes en lenguaje natural.
            chart_generator: Genera gráficos en base64.
            report_pdf_gen: Genera reportes en PDF.
            analyzers: Lista de implementaciones de estrategia IInsightAnalyzer.
        """
        self._metric_repo = metric_repo
        self._order_repo = order_repo
        self._response_generator = response_generator
        self._chart_generator = chart_generator
        self._report_pdf_gen = report_pdf_gen
        self._analyzers = analyzers
        settings = Settings.get_instance()
        self._sql_executor = SqliteExecutor(connection_path=settings.db_path)

    def generate_initial_insights(self) -> InitialInsightsResponse:
        """
        Ejecuta las 10 consultas predefinidas y genera un gráfico para cada una.

        Returns:
            InitialInsightsResponse con filas de datos de insights y gráficos en base64.
        """
        insights_data: list[dict] = []
        chart_b64_list: list[str] = []

        for query in self.INITIAL_QUERIES:
            title = query["title"]
            sql = query["sql"]
            chart_type_hint = query.get("chart_type", "")
            try:
                rows = self._sql_executor.execute(sql)
            except Exception as exc:
                logger.warning("Initial query '%s' failed: %s", title, exc)
                rows = []
            hint_title = f"[{chart_type_hint}] {title}" if chart_type_hint else title
            chart_b64 = self._chart_generator.generate_chart(hint_title, rows)
            insights_data.append({"title": title, "data": rows})
            chart_b64_list.append(chart_b64)

        return InitialInsightsResponse(
            insights_data=insights_data,
            chart_base64_list=chart_b64_list,
        )

    def generate_report_pdf(self, request: ReportPdfRequest) -> ReportPdfResponse:
        """
        Genera un reporte ejecutivo en PDF a partir de los datos de insights proporcionados.

        Args:
            request: ReportPdfRequest que contiene los insights y las rutas de los gráficos.

        Returns:
            ReportPdfResponse con el PDF codificado en base64.
        """
        insights: list[InsightResult] = []
        for item in request.insights:
            if isinstance(item, InsightResult):
                insights.append(item)
            elif isinstance(item, dict):
                try:
                    insights.append(
                        InsightResult(
                            category=item.get("category", "general"),
                            severity=item.get("severity", "info"),
                            title=item.get("title", ""),
                            description=item.get("description", ""),
                            recommendation=item.get("recommendation", ""),
                            affected_zones=item.get("affected_zones", []),
                            metadata=item.get("metadata", {}),
                        )
                    )
                except Exception as exc:
                    logger.warning("Could not parse insight item: %s", exc)

        pdf_bytes = self._report_pdf_gen.generate_pdf(
            insights=insights,
            charts=request.chart_paths,
            title=request.report_title,
        )
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        filename = f"rappi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        generated_at = datetime.now().isoformat()
        return ReportPdfResponse(
            pdf_base64=pdf_b64,
            filename=filename,
            generated_at=generated_at,
        )
