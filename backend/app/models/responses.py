# app/models/responses.py
"""Modelos de respuesta (response) de Pydantic para la API de Rappi Insights."""

from typing import Any, Optional
from pydantic import BaseModel


class ChatResponse(BaseModel):
    """Cuerpo de respuesta del endpoint de chat."""

    session_id: str
    bot_response: str
    chart_base64: Optional[str] = None
    status_code: int = 200


class InsightReportResponse(BaseModel):
    """Cuerpo de respuesta que contiene un reporte de insights generado."""

    executive_summary: str
    insights: list[Any] = []
    chart_base64_list: list[str] = []
    generated_at: str


class ReportPdfResponse(BaseModel):
    """Cuerpo de respuesta que contiene un reporte PDF generado."""

    pdf_base64: str
    filename: str
    generated_at: str


class ChatHistoryPdfResponse(BaseModel):
    """Cuerpo de respuesta que contiene el historial de chat exportado como PDF."""

    pdf_base64: str
    filename: str


class ErrorResponse(BaseModel):
    """Cuerpo de respuesta estándar para errores."""

    status_code: int
    detail: str
    error_type: str


class InitialInsightsResponse(BaseModel):
    """Cuerpo de respuesta que contiene los 10 insights iniciales precomputados."""

    insights_data: list[dict] = []
    chart_base64_list: list[str] = []
