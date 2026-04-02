# app/repositories/sqlite_metric_repository.py
"""Implementación del repositorio de métricas usando SQLite."""

import sqlite3
import logging
import pandas as pd
from app.interfaces.i_metric_repository import IMetricRepository
from app.entities.metric_record import MetricRecord
from app.entities.zone_info import ZoneInfo

logger = logging.getLogger(__name__)

WEEKLY_COLS = [
    "L8W_ROLL", "L7W_ROLL", "L6W_ROLL", "L5W_ROLL",
    "L4W_ROLL", "L3W_ROLL", "L2W_ROLL", "L1W_ROLL", "L0W_ROLL",
]


class SqliteMetricRepository(IMetricRepository):
    """
    Repositorio basado en SQLite para registros de métricas operativas.

    Carga datos desde un archivo Excel o CSV en una tabla SQLite en memoria
    al momento de la inicialización y proporciona métodos de consulta filtrada.
    """

    def __init__(self, db_path: str, csv_path: str) -> None:
        """
        Inicializa el repositorio, se conecta a SQLite y carga los datos.

    Args:
        db_path: Ruta al archivo de base de datos SQLite.
        csv_path: Ruta al archivo de datos en Excel (.xlsx) o CSV.
        """
        self._db_path = db_path
        self._csv_path = csv_path
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._load_excel_to_db()

    def _load_excel_to_db(self) -> None:
        """Lee el archivo fuente y carga las métricas en la tabla 'metrics'."""
        try:
            if self._csv_path.lower().endswith((".xlsx", ".xls")):
                df = pd.read_excel(self._csv_path, sheet_name="RAW_INPUT_METRICS")
            else:
                df = pd.read_csv(self._csv_path)
            df.columns = [c.strip().upper().replace(" ", "_") for c in df.columns]
            text_cols = ["COUNTRY", "CITY", "ZONE", "ZONE_TYPE", "ZONE_PRIORITIZATION", "METRIC"]
            float_cols = ["L8W_ROLL", "L7W_ROLL", "L6W_ROLL", "L5W_ROLL", "L4W_ROLL",
                          "L3W_ROLL", "L2W_ROLL", "L1W_ROLL", "L0W_ROLL"]
            dtype = {col: "TEXT" for col in text_cols if col in df.columns}
            dtype.update({col: "REAL" for col in float_cols if col in df.columns})
            df.to_sql("metrics", self._connection, if_exists="replace", index=False, dtype=dtype)
            self._connection.commit()
            logger.info("Metrics table loaded with %d rows.", len(df))
        except Exception as exc:
            logger.error("Failed to load metrics data: %s", exc)
            raise

    def _parse_record(self, row: tuple, columns: list[str]) -> MetricRecord:
        """
        Convierte una fila cruda de SQLite en un objeto de dominio MetricRecord.

        Args:
            row: Tupla de valores proveniente del cursor de la base de datos.
            columns: Nombres de columnas correspondientes a cada posición en row.

        Returns:
            Instancia de MetricRecord completamente poblada.
        """
        row_dict = dict(zip(columns, row))
        zone_info = ZoneInfo(
            country=str(row_dict.get("COUNTRY", "")),
            city=str(row_dict.get("CITY", "")),
            zone=str(row_dict.get("ZONE", "")),
            zone_type=str(row_dict.get("ZONE_TYPE", "")),
            zone_prioritization=str(row_dict.get("ZONE_PRIORITIZATION", "")),
        )
        weekly_values: list[float] = []
        for col in WEEKLY_COLS:
            try:
                weekly_values.append(float(row_dict.get(col, 0) or 0))
            except (TypeError, ValueError):
                weekly_values.append(0.0)
        return MetricRecord(
            zone_info=zone_info,
            metric_name=str(row_dict.get("METRIC", "")),
            weekly_values=weekly_values,
        )

    def _fetch(self, sql: str, params: tuple = ()) -> list[MetricRecord]:
        """Ejecuta un SELECT y convierte cada fila en objetos MetricRecord."""
        try:
            cursor = self._connection.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            return [self._parse_record(row, columns) for row in cursor.fetchall()]
        except Exception as exc:
            logger.error("Query failed: %s — %s", sql, exc)
            return []

    def get_all(self) -> list[MetricRecord]:
        """Retorna todos los registros de métricas desde la base de datos."""
        return self._fetch("SELECT * FROM metrics")

    def get_by_country(self, country: str) -> list[MetricRecord]:
        """
        Retorna registros de métricas para el país indicado.

        Args:
            country: Código de país de dos letras.
        """
        return self._fetch(
            "SELECT * FROM metrics WHERE UPPER(COUNTRY) = UPPER(?)", (country,)
        )

    def get_by_zone(self, zone: str) -> list[MetricRecord]:
        """
        Retorna registros de métricas para la zona indicada.

        Args:
            zone: Nombre de la zona.
        """
        return self._fetch(
            "SELECT * FROM metrics WHERE UPPER(ZONE) = UPPER(?)", (zone,)
        )

    def get_by_metric_name(self, metric: str) -> list[MetricRecord]:
        """
        Retorna registros de una métrica específica en todas las zonas.

        Args:
            metric: Nombre de la métrica.
        """
        return self._fetch(
            "SELECT * FROM metrics WHERE UPPER(METRIC) = UPPER(?)", (metric,)
        )

    def filter_metrics(
        self,
        country: str = "",
        city: str = "",
        zone: str = "",
        metric: str = "",
    ) -> list[MetricRecord]:
        """
        Retorna registros que coinciden con todos los criterios de filtro proporcionados (no vacíos).

        Args:
            country: Filtro opcional por país.
            city: Filtro opcional por ciudad.
            zone: Filtro opcional por zona.
            metric: Filtro opcional por nombre de la métrica.
        """
        clauses: list[str] = []
        params: list[str] = []
        if country:
            clauses.append("UPPER(COUNTRY) = UPPER(?)")
            params.append(country)
        if city:
            clauses.append("UPPER(CITY) = UPPER(?)")
            params.append(city)
        if zone:
            clauses.append("UPPER(ZONE) = UPPER(?)")
            params.append(zone)
        if metric:
            clauses.append("UPPER(METRIC) = UPPER(?)")
            params.append(metric)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        return self._fetch(f"SELECT * FROM metrics{where}", tuple(params))
