# tests/test_insight_router.py
"""Integration tests for the insight router using FastAPI TestClient."""

import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.insight_router import InsightRouter
from app.models.responses import InitialInsightsResponse, ReportPdfResponse
from datetime import datetime


def _build_app() -> tuple[FastAPI, MagicMock]:
    """Create a minimal FastAPI app with a mocked InsightService."""
    mock_service = MagicMock()
    mock_service.generate_initial_insights.return_value = InitialInsightsResponse(
        insights_data=[{"title": f"Insight {i}", "data": []} for i in range(10)],
        chart_base64_list=["base64chart==" for _ in range(10)],
    )
    mock_service.generate_report_pdf.return_value = ReportPdfResponse(
        pdf_base64="base64pdf==",
        filename="rappi_report.pdf",
        generated_at=datetime.now().isoformat(),
    )

    router = InsightRouter(insight_service=mock_service)
    app = FastAPI()
    app.include_router(router.router, prefix="/api/v1")
    return app, mock_service


@pytest.fixture()
def client_and_service():
    app, service = _build_app()
    return TestClient(app), service


class TestInsightRouter:
    """Integration tests for InsightRouter endpoints."""

    def test_get_initial_insights_returns_200(self, client_and_service):
        """GET /insights/initial should return 200 with 10 insights."""
        client, _ = client_and_service
        response = client.get("/api/v1/insights/initial")
        assert response.status_code == 200
        data = response.json()
        assert len(data["insights_data"]) == 10
        assert len(data["chart_base64_list"]) == 10

    def test_generate_report_pdf_returns_201(self, client_and_service):
        """POST /insights/report-pdf should return 201 with pdf_base64."""
        client, _ = client_and_service
        response = client.post(
            "/api/v1/insights/report-pdf",
            json={
                "insights": [],
                "chart_paths": [],
                "report_title": "Test Report",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["pdf_base64"] == "base64pdf=="

    def test_get_categories_returns_200(self, client_and_service):
        """GET /insights/categories should return the 4 analyzer categories."""
        client, _ = client_and_service
        response = client.get("/api/v1/insights/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 4
