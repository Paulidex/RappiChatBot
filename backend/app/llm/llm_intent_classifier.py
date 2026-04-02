# app/llm/llm_intent_classifier.py
"""Clasificador de intención basado en LLM para mensajes de chat de Flash (backend Gemini)."""

import json
import logging
from google import genai
from app.interfaces.i_intent_classifier import IIntentClassifier
from app.entities.query_intent import QueryIntent

logger = logging.getLogger(__name__)


class LlmIntentClassifier(IIntentClassifier):
    """
    Clasifica los mensajes del usuario en intenciones 'chart', 'query' o 'general'
    utilizando Google Gemini.

    El modelo retorna un objeto JSON con intent_type y extracted_filters,
    el cual se convierte en una entidad QueryIntent.
    """

    def __init__(self, api_key: str, model_name: str) -> None:
        """
        Inicializa el clasificador con credenciales de Gemini.

        Args:
            api_key: Clave API de Gemini.
            model_name: Identificador del modelo Gemini (por ejemplo: 'gemini-1.5-flash').
        """
        self._api_key = api_key
        self._model_name = model_name
        self._client = genai.Client(api_key=api_key)

    def _build_classification_prompt(self, message: str) -> str:
        """
        Construye el prompt utilizado para clasificar el mensaje del usuario.

        Args:
            message: Mensaje en bruto del usuario.

        Returns:
            Cadena de prompt para Gemini.
        """
        return (
            "Eres un clasificador de intenciones para Flash, el bot de análisis de Rappi.\n"
            "Clasifica el mensaje del usuario en UNA de estas tres categorías:\n\n"
            "- \"chart\": el usuario pide una gráfica, grafica, muestra gráfico, "
            "visualiza, dibuja, plotea, evolución visual, compara visualmente, "
            "o quiere ver algo de forma gráfica.\n"
            "- \"query\": el usuario pide datos, números, filtros, rankings, "
            "top N, promedios, cuáles, cuántos, lista, tabla de resultados.\n"
            "- \"general\": saludos, preguntas conceptuales, qué significa una métrica, "
            "contexto conversacional, 'cómo te llamas', referencias a mensajes previos, "
            "preguntas que no requieren consultar la base de datos.\n\n"
            "También extrae filtros relevantes del mensaje (country, city, zone, metric, top_n).\n\n"
            "Responde ÚNICAMENTE con un JSON válido sin markdown:\n"
            "{\"intent_type\": \"chart|query|general\", "
            "\"extracted_filters\": {\"country\": \"\", \"city\": \"\", "
            "\"zone\": \"\", \"metric\": \"\", \"top_n\": null}}\n\n"
            f"Mensaje del usuario: {message}"
        )

    def classify(self, user_message: str) -> QueryIntent:
        """
        Clasifica la intención de un mensaje del usuario mediante Gemini.

        En caso de error, retorna por defecto una intención 'general'.

        Args:
            user_message: Texto en bruto del usuario.

        Returns:
            QueryIntent con intent_type y filtros extraídos.
        """
        try:
            prompt = self._build_classification_prompt(user_message)
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt,
            )
            raw = (response.text or "").strip()
            raw = raw.strip("```json").strip("```").strip()
            data = json.loads(raw)
            return QueryIntent(
                intent_type=data.get("intent_type", "general"),
                original_question=user_message,
                extracted_filters=data.get("extracted_filters", {}),
            )
        except Exception as exc:
            logger.error("Clasificación de intención fallida: %s", exc)
            return QueryIntent(
                intent_type="general",
                original_question=user_message,
                extracted_filters={},
            )
