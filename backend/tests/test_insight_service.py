# tests/test_insight_service.py
"""Unit tests for InsightService."""

import pytest
from unittest.mock import MagicMock, patch
from app.services.insight_service import InsightService
from app.entities.metric_record import MetricRecord
from app.entities.order_record import OrderRecord
from app.entities.zone_info import ZoneInfo
from app.entities.insight_result import InsightResult
from app.analyzers.anomaly_analyzer import AnomalyAnalyzer
from app.analyzers.trend_analyzer import TrendAnalyzer
from app.models.requests import ReportPdfRequest
from app.models.responses import InitialInsightsResponse, ReportPdfResponse


def _zone(country: str = "CO", zone: str = "ZoneA") -> ZoneInfo:
    return ZoneInfo(
        country=country, city="Bogota", zone=zone,
        zone_type="Wealthy", zone_prioritization="High Priority"
    )


def _metric(weekly_values: list[float], metric: str = "Lead Penetration") -> MetricRecord:
    return MetricRecord(
        zone_info=_zone(), metric_name=metric, weekly_values=weekly_values
    )


def _make_service() -> InsightService:
    metric_repo = MagicMock()
    order_repo = MagicMock()
    response_generator = MagicMock()
    response_generator.generate.return_value = "Summary"
    chart_generator = MagicMock()
    chart_generator.generate_chart.return_value = "base64chart=="
    report_pdf_gen = MagicMock()
    report_pdf_gen.generate_pdf.return_value = b"%PDF-fake"
    analyzers = [AnomalyAnalyzer(threshold=0.10), TrendAnalyzer(min_consecutive_weeks=3)]

    with patch("app.services.insight_service.SqliteExecutor") as mock_exec_cls:
        executor = MagicMock()
        executor.execute.return_value = [{"ZONE": "ZoneA", "value": 1}]
        mock_exec_cls.return_value = executor
        service = InsightService(
            metric_repo=metric_repo,
            order_repo=order_repo,
            response_generator=response_generator,
            chart_generator=chart_generator,
            report_pdf_gen=report_pdf_gen,
            analyzers=analyzers,
        )
    return service


class TestInsightService:
    """Unit tests for InsightService."""

    def test_generate_initial_insights(self):
        """generate_initial_insights must return exactly 10 insights with charts."""
        service = _make_service()
        result = service.generate_initial_insights()
        assert isinstance(result, InitialInsightsResponse)
        assert len(result.insights_data) == 10

    def test_insight_charts_generated(self):
        """generate_initial_insights must produce 10 chart entries."""
        service = _make_service()
        result = service.generate_initial_insights()
        assert len(result.chart_base64_list) == 10

    def test_anomaly_detection_above_threshold(self):
        """AnomalyAnalyzer must flag a record with >10% WoW change."""
        analyzer = AnomalyAnalyzer(threshold=0.10)
        record = _metric([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.5])
        results = analyzer.analyze([record], [])
        assert len(results) >= 1
        assert results[0].category == "anomaly"

    def test_trend_detection_consecutive_weeks(self):
        """TrendAnalyzer must flag a record with 3+ consecutive declining weeks."""
        analyzer = TrendAnalyzer(min_consecutive_weeks=3)
        record = _metric([10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0])
        results = analyzer.analyze([record], [])
        assert len(results) >= 1
        assert results[0].category == "trend"

    def test_generate_report_pdf(self):
        """generate_report_pdf must return a ReportPdfResponse with pdf_base64."""
        service = _make_service()
        request = ReportPdfRequest(
            insights=[
                {
                    "category": "anomaly",
                    "severity": "critical",
                    "title": "Test",
                    "description": "desc",
                    "recommendation": "rec",
                }
            ],
            chart_paths=["base64chart=="],
            report_title="Test Report",
        )
        result = service.generate_report_pdf(request)
        assert isinstance(result, ReportPdfResponse)
        assert result.pdf_base64 != ""
        assert result.filename.endswith(".pdf")
