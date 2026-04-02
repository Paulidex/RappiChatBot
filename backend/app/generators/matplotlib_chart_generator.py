# app/generators/matplotlib_chart_generator.py
"""Generador de gráficos basado en Matplotlib para visualizaciones de datos de Flash."""

import base64
import io
import logging
from typing import Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.figure

from app.interfaces.i_chart_generator import IChartGenerator

logger = logging.getLogger(__name__)

RAPPI_ORANGE = "#B5541A"
RAPPI_DARK = "#2C1A0E"
CHART_COLORS = [
    "#B5541A", "#8B3D12", "#C4783A", "#7A5C3A",
    "#5C3D1E", "#A07040", "#6B4226", "#D4956A",
    "#4A2E1A", "#E8B48A",
]


class MatplotlibChartGenerator(IChartGenerator):
    """
    Genera gráficos de barras o líneas a partir de datos de consultas usando Matplotlib.

    El tipo de gráfico se infiere a partir de palabras clave en la pregunta del usuario.
    Todos los gráficos se codifican como cadenas PNG en base64.
    """

    def _select_chart_type(self, question: str, data: list[dict]) -> str:
        """
        Determina el tipo de gráfico más apropiado combinando palabras clave
        de la pregunta con heurísticas sobre la estructura de los datos.

        Args:
            question: Pregunta original del usuario.
            data: Filas del resultado de la consulta.

        Returns:
            'line', 'pie', 'horizontal_bar' o 'bar'.
        """
        import re  # noqa: PLC0415
        hint_match = re.match(r"^\[(line|bar|horizontal_bar|pie)\]", question.strip())
        if hint_match:
            return hint_match.group(1)
        q = question.lower()

        line_keywords = [
            "evolución", "evolucion", "tendencia", "últimas semanas",
            "ultimas semanas", "semana", "semanal", "histórico", "historico",
            "tiempo", "progresión", "progresion", "a lo largo", "por semana",
            "8 semanas", "semanas",
        ]
        pie_keywords = [
            "distribución", "distribucion", "proporción", "proporcion",
            "participación", "participacion", "porcentaje de", "% de",
            "composición", "composicion", "reparto", "share",
            "wealthy vs", "vs non",
        ]
        hbar_keywords = [
            "ranking", "top", "mejores", "peores", "mayor", "menor",
            "más alto", "más bajo", "mas alto", "mas bajo",
            "variación", "variacion", "desviación", "desviacion",
            "caídas", "caidas", "anomalías", "anomalias",
            "velocidad", "wow", "ciudades por",
        ]

        for kw in line_keywords:
            if kw in q:
                return "line"

        for kw in pie_keywords:
            if kw in q:
                if data and len(data) <= 8:
                    return "pie"

        # Barras horizontales para rankings o etiquetas largas
        if data:
            keys = list(data[0].keys())
            first_labels = [str(row.get(keys[0], "")) for row in data]
            avg_label_len = sum(len(l) for l in first_labels) / max(len(first_labels), 1)
            has_ranking_kw = any(kw in q for kw in hbar_keywords)
            if has_ranking_kw or avg_label_len > 15:
                return "horizontal_bar"

        return "bar"

    def _create_pie_chart(
        self,
        data: list[dict],
        config: dict[str, Any],
    ) -> matplotlib.figure.Figure:
        """
        Crea un gráfico de pastel para mostrar distribuciones o proporciones.

        Args:
            data: Filas de datos; primera columna = etiqueta, segunda = valor.
            config: Diccionario con clave 'title'.

        Returns:
            Objeto Figure de Matplotlib.
        """
        if not data:
            fig, ax = plt.subplots(figsize=(7, 5))
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            return fig

        keys = list(data[0].keys())
        label_col = keys[0]
        value_col = keys[1] if len(keys) > 1 else keys[0]

        labels = [str(row.get(label_col, ""))[:20] for row in data]
        try:
            values = [abs(float(row.get(value_col, 0) or 0)) for row in data]
        except (TypeError, ValueError):
            values = [1.0] * len(data)

        colors = (CHART_COLORS * ((len(data) // len(CHART_COLORS)) + 1))[: len(data)]
        fig, ax = plt.subplots(figsize=(8, 6))
        pie_result = ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=140,
            textprops={"fontsize": 8},
        )
        if len(pie_result) == 3:
            for at in pie_result[2]:
                at.set_fontsize(8)
                at.set_color("white")
        ax.set_title(config.get("title", "Distribución"), fontsize=13, fontweight="bold")
        fig.patch.set_facecolor("#FDF8F3")
        plt.tight_layout()
        return fig

    def _create_horizontal_bar_chart(
        self,
        data: list[dict],
        config: dict[str, Any],
    ) -> matplotlib.figure.Figure:
        """
        Crea un gráfico de barras horizontal, ideal para rankings con etiquetas largas.

        Args:
            data: Filas de datos; primera columna = etiqueta, segunda = valor.
            config: Diccionario con claves 'title', 'xlabel'.

        Returns:
            Objeto Figure de Matplotlib.
        """
        if not data:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            return fig

        keys = list(data[0].keys())
        label_col = keys[0]
        value_col = keys[1] if len(keys) > 1 else keys[0]

        labels = [str(row.get(label_col, ""))[:30] for row in data]
        try:
            values = [float(row.get(value_col, 0) or 0) for row in data]
        except (TypeError, ValueError):
            values = list(range(len(data)))

        # Ordenar de mayor a menor
        paired = sorted(zip(values, labels), reverse=True)
        values, labels = zip(*paired) if paired else ([], [])

        height = max(4, len(labels) * 0.45)
        fig, ax = plt.subplots(figsize=(10, height))
        colors = [RAPPI_ORANGE if v >= 0 else "#6B2A0A" for v in values]
        bars = ax.barh(range(len(labels)), values, color=colors, edgecolor="white")
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=9)
        ax.invert_yaxis()
        ax.set_title(config.get("title", "Ranking"), fontsize=13, fontweight="bold")
        ax.set_xlabel(config.get("xlabel", value_col), fontsize=10)
        ax.set_facecolor("#FAF5EF")
        fig.patch.set_facecolor("#FDF8F3")
        ax.axvline(x=0, color="gray", linewidth=0.8)
        for bar, val in zip(bars, values):
            ax.text(
                val + (max(values) * 0.01 if values else 0),
                bar.get_y() + bar.get_height() / 2,
                f"{val:,.2f}",
                va="center",
                fontsize=8,
            )
        plt.tight_layout()
        return fig

    def _create_bar_chart(
        self,
        data: list[dict],
        config: dict[str, Any],
    ) -> matplotlib.figure.Figure:
        """
        Crea un gráfico de barras horizontal o vertical.

        Args:
            data: Filas de datos a visualizar.
            config: Diccionario con claves 'title', 'xlabel', 'ylabel'.

        Returns:
            Objeto Figure de Matplotlib.
        """
        if not data:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            return fig

        keys = list(data[0].keys())
        label_col = keys[0]
        value_col = keys[1] if len(keys) > 1 else keys[0]

        labels = [str(row.get(label_col, ""))[:20] for row in data]
        try:
            values = [float(row.get(value_col, 0) or 0) for row in data]
        except (TypeError, ValueError):
            values = list(range(len(data)))

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(range(len(labels)), values, color=RAPPI_ORANGE, edgecolor="white")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=9)
        ax.set_title(config.get("title", "Resultados"), fontsize=13, fontweight="bold")
        ax.set_ylabel(config.get("ylabel", value_col), fontsize=10)
        ax.set_facecolor("#FAF5EF")
        fig.patch.set_facecolor("#FDF8F3")
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{val:,.1f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        plt.tight_layout()
        return fig

    def _create_line_chart(
        self,
        data: list[dict],
        config: dict[str, Any],
    ) -> matplotlib.figure.Figure:
        """
        Crea un gráfico de líneas con múltiples series.

        Args:
            data: Filas de datos; la primera columna se usa como etiqueta de la serie.
            config: Diccionario con claves 'title', 'xlabel', 'ylabel'.

        Returns:
            Objeto Figure de Matplotlib.
        """
        if not data:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            return fig

        keys = list(data[0].keys())
        label_col = keys[0]
        value_cols = keys[1:]

        fig, ax = plt.subplots(figsize=(11, 5))
        for idx, row in enumerate(data):
            label = str(row.get(label_col, f"Serie {idx + 1}"))
            y_vals: list[float] = []
            for vc in value_cols:
                try:
                    y_vals.append(float(row.get(vc, 0) or 0))
                except (TypeError, ValueError):
                    y_vals.append(0.0)
            color = CHART_COLORS[idx % len(CHART_COLORS)]
            ax.plot(value_cols, y_vals, marker="o", label=label, color=color)

        ax.set_title(config.get("title", "Evolución temporal"), fontsize=13, fontweight="bold")
        ax.set_xlabel(config.get("xlabel", "Semana"), fontsize=10)
        ax.set_ylabel(config.get("ylabel", "Valor"), fontsize=10)
        ax.legend(fontsize=8, loc="best")
        ax.set_facecolor("#FAF5EF")
        fig.patch.set_facecolor("#FDF8F3")
        plt.xticks(rotation=30, ha="right", fontsize=8)
        plt.tight_layout()
        return fig

    def _encode_to_base64(self, figure: matplotlib.figure.Figure) -> str:
        """
        Guarda una figura de Matplotlib en un buffer PNG y la codifica en base64.

        Args:
            figure: La figura de Matplotlib a codificar.

        Returns:
            Cadena PNG codificada en base64.
        """
        buf = io.BytesIO()
        figure.savefig(buf, format="png", dpi=120, bbox_inches="tight")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(figure)
        return encoded

    def generate_chart(self, question: str, data: list[dict]) -> str:
        """
        Genera un gráfico a partir de datos y lo retorna como una cadena PNG en base64.

        Args:
            question: Pregunta del usuario (usada para inferir tipo de gráfico y título).
            data: Filas del resultado de la consulta a visualizar.

        Returns:
            Cadena PNG codificada en base64. Retorna una cadena vacía en caso de error.
        """
        try:
            if not data:
                fig, ax = plt.subplots(figsize=(6, 3))
                ax.text(0.5, 0.5, "No hay datos para graficar", ha="center", va="center")
                ax.axis("off")
                return self._encode_to_base64(fig)

            chart_type = self._select_chart_type(question, data)
            import re as _re
            clean_question = _re.sub(r"^\[(line|bar|horizontal_bar|pie)\]\s*", "", question.strip())
            title = clean_question[:60] + ("…" if len(clean_question) > 60 else "")
            config = {"title": title, "xlabel": "Semana", "ylabel": "Valor"}

            if chart_type == "line":
                fig = self._create_line_chart(data, config)
            elif chart_type == "pie":
                fig = self._create_pie_chart(data, config)
            elif chart_type == "horizontal_bar":
                fig = self._create_horizontal_bar_chart(data, config)
            else:
                fig = self._create_bar_chart(data, config)

            return self._encode_to_base64(fig)
        except Exception as exc:
            logger.error("Chart generation failed: %s", exc)
            return ""
