# app/repositories/sqlite_order_repository.py
"""Implementación del repositorio de órdenes usando SQLite."""

import sqlite3
import logging
import pandas as pd
from app.interfaces.i_order_repository import IOrderRepository
from app.entities.order_record import OrderRecord
from app.entities.zone_info import ZoneInfo

logger = logging.getLogger(__name__)

WEEKLY_COLS = ["L8W", "L7W", "L6W", "L5W", "L4W", "L3W", "L2W", "L1W", "L0W"]


class SqliteOrderRepository(IOrderRepository):
    """
    Repositorio basado en SQLite para registros de volumen de pedidos por zona.

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
        """Lee el archivo fuente y carga las órdenes en la tabla 'orders'."""
        try:
            if self._csv_path.lower().endswith((".xlsx", ".xls")):
                df = pd.read_excel(self._csv_path, sheet_name="RAW_ORDERS")
            else:
                df = pd.read_csv(self._csv_path)
            df.columns = [c.strip().upper().replace(" ", "_") for c in df.columns]
            text_cols = ["COUNTRY", "CITY", "ZONE", "METRIC"]
            float_cols = ["L8W", "L7W", "L6W", "L5W", "L4W", "L3W", "L2W", "L1W", "L0W"]
            dtype = {col: "TEXT" for col in text_cols if col in df.columns}
            dtype.update({col: "REAL" for col in float_cols if col in df.columns})
            df.to_sql("orders", self._connection, if_exists="replace", index=False, dtype=dtype)
            self._connection.commit()
            logger.info("Orders table loaded with %d rows.", len(df))
        except Exception as exc:
            logger.error("Failed to load orders data: %s", exc)
            raise

    def _parse_record(self, row: tuple, columns: list[str]) -> OrderRecord:
        """
        Convierte una fila cruda de SQLite en un objeto de dominio OrderRecord.

        Args:
            row: Tupla de valores proveniente del cursor de la base de datos.
            columns: Nombres de columnas correspondientes a cada posición en row.

        Returns:
            Instancia de OrderRecord completamente poblada.
        """
        row_dict = dict(zip(columns, row))
        zone_info = ZoneInfo(
            country=str(row_dict.get("COUNTRY", "")),
            city=str(row_dict.get("CITY", "")),
            zone=str(row_dict.get("ZONE", "")),
            zone_type=str(row_dict.get("ZONE_TYPE", "")),
            zone_prioritization=str(row_dict.get("ZONE_PRIORITIZATION", "")),
        )
        weekly_orders: list[float] = []
        for col in WEEKLY_COLS:
            try:
                weekly_orders.append(float(row_dict.get(col, 0) or 0))
            except (TypeError, ValueError):
                weekly_orders.append(0.0)
        return OrderRecord(zone_info=zone_info, weekly_orders=weekly_orders)

    def _fetch(self, sql: str, params: tuple = ()) -> list[OrderRecord]:
        """Ejecuta un SELECT y convierte cada fila en objetos OrderRecord."""
        try:
            cursor = self._connection.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            return [self._parse_record(row, columns) for row in cursor.fetchall()]
        except Exception as exc:
            logger.error("Query failed: %s — %s", sql, exc)
            return []

    def get_all(self) -> list[OrderRecord]:
        """Retorna todos los registros de órdenes desde la base de datos."""
        return self._fetch("SELECT * FROM orders")

    def get_by_country(self, country: str) -> list[OrderRecord]:
        """
        Retorna registros de órdenes para el país indicado.

        Args:
            country: Código de país de dos letras.
        """
        return self._fetch(
            "SELECT * FROM orders WHERE UPPER(COUNTRY) = UPPER(?)", (country,)
        )

    def get_by_zone(self, zone: str) -> list[OrderRecord]:
        """
        Retorna registros de órdenes para la zona indicada.

        Args:
            zone: Nombre de la zona.
        """
        return self._fetch(
            "SELECT * FROM orders WHERE UPPER(ZONE) = UPPER(?)", (zone,)
        )

    def get_top_growing_zones(self, n: int, weeks: int) -> list[OrderRecord]:
        """
        etorna las N zonas principales ordenadas por crecimiento de órdenes en las últimas N semanas.

        Utiliza la tasa de crecimiento entre L0W y L1W como criterio de ordenamiento.

        Args:
            n: Número de zonas principales a retornar.
            weeks: Número de semanas recientes a considerar (actualmente usa L0W/L1W).
        """
        sql = """
            SELECT *,
                   (L0W - L1W) * 1.0 / NULLIF(L1W, 0) AS _growth_rate
            FROM orders
            ORDER BY _growth_rate DESC
            LIMIT ?
        """
        try:
            cursor = self._connection.execute(sql, (n,))
            columns = [desc[0] for desc in cursor.description]
            return [self._parse_record(row, columns) for row in cursor.fetchall()]
        except Exception as exc:
            logger.error("get_top_growing_zones failed: %s", exc)
            return []
