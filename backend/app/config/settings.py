# app/config/settings.py
"""Módulo de configuración que utiliza el patrón Singleton para la configuración de la aplicación."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Settings:
    """
    Configuraciones de la aplicación cargadas desde variables de entorno.

    Implementa el patrón Singleton para garantizar una única instancia
    de configuración durante todo el ciclo de vida de la aplicación.
    """

    _instance: Optional["Settings"] = None

    def __init__(self) -> None:
        """Inicializa la configuración cargando variables de entorno."""
        load_dotenv()
        self.llm_api_key: str = os.getenv("GEMINI_API", os.getenv("LLM_API_KEY", ""))
        self.llm_model_name: str = os.getenv("LLM_MODEL_NAME", "gemini-1.5-flash")
        self.db_path: str = os.getenv("DB_PATH", "data/rappi_insights.db")
        self.metric_file_path: str = os.getenv("METRIC_FILE_PATH", "")
        self.order_file_path: str = os.getenv("ORDER_FILE_PATH", "")
        self._validate_file_paths()
        self.anomaly_threshold: float = float(
            os.getenv("ANOMALY_THRESHOLD", "0.10")
        )
        self.trend_min_weeks: int = int(os.getenv("TREND_MIN_WEEKS", "3"))
        logger.info("Settings cargados correctamente.")

    def _validate_file_paths(self) -> None:
        """Valida que las rutas de archivos de datos existan en el sistema."""
        for env_var, path in (
            ("METRIC_FILE_PATH", self.metric_file_path),
            ("ORDER_FILE_PATH", self.order_file_path),
        ):
            if not path:
                raise FileNotFoundError(
                    f"La variable de entorno '{env_var}' no está configurada en el .env"
                )
            if not os.path.isfile(path):
                raise FileNotFoundError(
                    f"El archivo especificado en '{env_var}' no fue encontrado: '{path}'"
                )

    @classmethod
    def get_instance(cls) -> "Settings":
        """
        Retorna la instancia única (singleton) de Settings, creándola si es necesario.

        Carga la configuración desde el archivo .env en la primera llamada.

        Returns:
            Settings: La instancia única de Settings.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
