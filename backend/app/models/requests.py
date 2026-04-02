# app/models/requests.py
"""Modelos de solicitud (request) de Pydantic para la API de Rappi Insights."""

from typing import Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Cuerpo de solicitud para el endpoint de chat."""

    session_id: str
    user_message: str


class InsightReportRequest(BaseModel):
    """Cuerpo de solicitud para generar un reporte de insights."""

    categories: list[str] = []
    country_filter: str = ""
    top_n: int = 5


class ReportPdfRequest(BaseModel):
    """Cuerpo de solicitud para generar un reporte en PDF a partir de insights."""

    insights: list[Any] = []
    chart_paths: list[str] = []
    report_title: str = "Reporte de Insights - Rappi"


class ChatHistoryPdfRequest(BaseModel):
    """Cuerpo de solicitud para exportar el historial de chat como PDF."""

    session_id: str
