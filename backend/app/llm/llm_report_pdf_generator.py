# app/llm/llm_report_pdf_generator.py
"""Generador de PDF para reportes ejecutivos usando Gemini como LLM."""

import base64
import io
import json
import logging
from datetime import datetime
from google import genai
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from app.interfaces.i_report_pdf_generator import IReportPdfGenerator
from app.entities.insight_result import InsightResult

logger = logging.getLogger(__name__)


class LlmReportPdfGenerator(IReportPdfGenerator):
    """
    Genera PDFs de reportes ejecutivos profesionales mediante:
    1. Envío de insights a Gemini para la generación del texto narrativo.
    2. Renderizado del texto junto con las gráficas en un PDF usando fpdf2.
    """

    def __init__(self, api_key: str, model_name: str) -> None:
        """
        Inicializa el generador de PDF de reportes.

        Args:
            api_key: Clave API de Gemini.
            model_name: Identificador del modelo Gemini.
        """
        self._api_key = api_key
        self._model_name = model_name
        self._client = genai.Client(api_key=api_key)

    def _build_report_prompt(self, insights: list[InsightResult]) -> str:
        """
        Construye el prompt que le pide a Gemini redactar el reporte ejecutivo.

        Args:
            insights: Lista de objetos InsightResult a incluir.

        Returns:
            Cadena de texto del prompt formateado.
        """
        try:
            insights_data = [
                {
                    "category": i.category,
                    "severity": i.severity,
                    "title": i.title,
                    "description": i.description,
                    "recommendation": i.recommendation,
                    "affected_zones": i.affected_zones,
                }
                for i in insights
            ]
            insights_str = json.dumps(insights_data, ensure_ascii=False, indent=2)
        except Exception:
            insights_str = str(insights)
        return (
            "Eres un analista senior de Rappi. Genera un reporte ejecutivo profesional.\n"
            "El reporte debe contener:\n"
            "1. Resumen ejecutivo (3-5 hallazgos más críticos)\n"
            "2. Detalle por categoría de insight\n"
            "3. Recomendaciones accionables para cada hallazgo\n\n"
            "Escribe en español, tono profesional y ejecutivo.\n\n"
            f"Insights:\n{insights_str}"
        )

    def _render_to_pdf(self, content: str, charts: list[str]) -> bytes:
        """
        Renderiza el texto narrativo y las gráficas en base64 dentro de un PDF.

        Args:
            content: Texto narrativo generado por Gemini.
            charts: Lista de imágenes PNG codificadas en base64.

        Returns:
            Archivo PDF como bytes en bruto.
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(255, 68, 31)
        pdf.cell(
            0, 12, "Reporte de Insights - Rappi",
            align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(
            0, 8,
            f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        pdf.ln(6)

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(0, 0, 0)
        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                pdf.set_font("Helvetica", "B", 13)
                pdf.multi_cell(0, 8, stripped.lstrip("#").strip())
                pdf.set_font("Helvetica", "", 11)
            elif stripped.startswith("**") and stripped.endswith("**"):
                pdf.set_font("Helvetica", "B", 11)
                pdf.multi_cell(0, 7, stripped.strip("*"))
                pdf.set_font("Helvetica", "", 11)
            else:
                pdf.multi_cell(0, 7, line)

        for idx, chart_b64 in enumerate(charts):
            try:
                image_bytes = base64.b64decode(chart_b64)
                image_buf = io.BytesIO(image_bytes)
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(
                    0, 10, f"Gráfica {idx + 1}",
                    new_x=XPos.LMARGIN, new_y=YPos.NEXT,
                )
                pdf.image(image_buf, x=10, w=190)
            except Exception as exc:
                logger.warning("No se pudo incrustar la gráfica %d: %s", idx, exc)

        return bytes(pdf.output())

    def generate_pdf(
        self,
        insights: list[InsightResult],
        charts: list[str],
        title: str,
    ) -> bytes:
        """
        Genera un reporte ejecutivo completo en PDF.

        Args:
            insights: Resultados de insights a incluir.
            charts: Imágenes de gráficas codificadas en base64.
            title: Título del reporte (usado en el contexto del prompt).

        Returns:
            Archivo PDF como bytes en bruto.
        """
        try:
            prompt = self._build_report_prompt(insights)
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt,
            )
            narrative = (response.text or "").strip()
        except Exception as exc:
            logger.error("Generación del reporte con Gemini falló: %s", exc)
            narrative = "Error al generar el contenido del reporte con el LLM."
        return self._render_to_pdf(narrative, charts)
