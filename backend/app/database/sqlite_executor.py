# app/database/sqlite_executor.py
"""Ejecutor SQL para SQLite con validación de solo lectura."""

import sqlite3
import logging
from app.interfaces.i_sql_executor import ISqlExecutor

logger = logging.getLogger("db")

FORBIDDEN_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "ATTACH", "DETACH",
}


class SqliteExecutor(ISqlExecutor):
    """
    Ejecuta consultas SQL SELECT validadas contra una base de datos SQLite.

    Solo se permiten sentencias SELECT; cualquier otra operación DML/DDL genera
    un ValueError antes de llegar a la base de datos.
    """

    def __init__(self, connection_path: str) -> None:
        """
        Inicializa el ejecutor y abre la conexión a SQLite.

        Args:
            connection_path: Ruta del archivo de la base de datos SQLite.
        """
        self._connection_path = connection_path
        self._connection = sqlite3.connect(
            connection_path, check_same_thread=False
        )
        logger.info("SqliteExecutor connected to %s", connection_path)

    def _validate_sql(self, sql: str) -> bool:
        """
        Retorna True solo si la sentencia es una consulta SELECT.

        Raises:
            ValueError: Si la sentencia contiene palabras clave prohibidas.

        Args:
            sql: Cadena SQL a validar.
        """
        normalised = sql.strip().upper()
        for keyword in FORBIDDEN_KEYWORDS:
            if keyword in normalised.split():
                raise ValueError(
                    f"Forbidden SQL keyword detected: {keyword}. "
                    "Only SELECT statements are allowed."
                )
        if not normalised.startswith("SELECT"):
            raise ValueError("Only SELECT statements are permitted.")
        return True

    def execute(self, sql: str) -> list[dict]:
        """
        Valida y ejecuta una consulta SQL SELECT.

        Args:
            sql: Sentencia SQL SELECT a ejecutar.

        Returns:
            Lista de filas donde cada fila es un diccionario con claves como nombres de columnas.

        Raises:
            ValueError: Si el SQL no es una sentencia SELECT válida.
        """
        self._validate_sql(sql)
        logger.info("SQL generado: %s", sql)
        try:
            cursor = self._connection.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            logger.info("SQL retornó %d filas. Columnas: %s", len(rows), columns)
            return [dict(zip(columns, row)) for row in rows]
        except Exception as exc:
            logger.error("SQL execution failed: %s | error: %s", sql, exc)
            raise

    def get_schema(self) -> str:
        """
        Retorna una sentencia CREATE TABLE (DDL) por cada consulta en la base de datos.

        Utilizado por el generador SQL basado en LLM para entender el esquema disponible.

        Returns:
            Sentencias CREATE TABLE concatenadas en una sola cadena.
        """
        try:
            cursor = self._connection.execute(
                "SELECT name, sql FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            parts: list[str] = []
            for name, ddl in cursor.fetchall():
                if ddl:
                    parts.append(ddl)
                else:
                    parts.append(f"-- table: {name} (no DDL available)")
            return "\n\n".join(parts)
        except Exception as exc:
            logger.error("get_schema failed: %s", exc)
            return ""
