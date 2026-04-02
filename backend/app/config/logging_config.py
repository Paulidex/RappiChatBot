# app/config/logging_config.py
"""Configuración centralizada de logging para Flash."""

import logging
import os
from logging.handlers import RotatingFileHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "..", "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging() -> None:
    """
    Configura el sistema de logging de la aplicación.

    - Consola: todos los niveles INFO+.
    - app.log: log general rotativo (5 MB, 5 copias).
    - chat.log, insight.log, db.log: logs por módulo (5 MB, 3 copias).
    """
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "app.log"),
        maxBytes=5_000_000,
        backupCount=5,
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    for module in ("chat", "insight", "db"):
        handler = RotatingFileHandler(
            os.path.join(LOG_DIR, f"{module}.log"),
            maxBytes=5_000_000,
            backupCount=3,
        )
        handler.setFormatter(formatter)

        module_logger = logging.getLogger(module)
        module_logger.setLevel(logging.INFO)
        module_logger.addHandler(handler)
        module_logger.propagate = True


def get_logger(name: str) -> logging.Logger:
    """
    Retorna un logger con el nombre indicado.

    Args:
        name: Nombre del logger (ej. 'chat', 'insight', 'db').

    Returns:
        Instancia de logging.Logger.
    """
    return logging.getLogger(name)
