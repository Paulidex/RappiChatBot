# app/llm/llm_response_generator.py
"""Generador de respuestas en lenguaje natural para Flash (backend Gemini)."""

import json
import logging
from google import genai
from app.interfaces.i_response_generator import IResponseGenerator

logger = logging.getLogger(__name__)


class LlmResponseGenerator(IResponseGenerator):
    """
    Genera respuestas en lenguaje natural en español utilizando Google Gemini.

    Cuando hay datos, el modelo actúa como analista financiero senior interpretando
    los resultados de la consulta. Cuando los datos están vacíos, responde de forma
    conversacional usando el historial de conversación incluido en la pregunta.
    """

    def __init__(self, api_key: str, model_name: str) -> None:
        """
        Inicializa el generador de respuestas.

        Args:
            api_key: Clave API de Gemini.
            model_name: Identificador del modelo Gemini.
        """
        self._api_key = api_key
        self._model_name = model_name
        self._client = genai.Client(api_key=api_key)

    def _build_analysis_prompt(self, question: str, data: list[dict]) -> str:
        """
        Construye un prompt para respuestas analíticas basadas en datos.

        Args:
            question: Pregunta original del usuario.
            data: Filas del resultado de la consulta a interpretar.

        Returns:
            Cadena de prompt formateada.
        """
        try:
            data_str = json.dumps(data, ensure_ascii=False, indent=2)
        except Exception:
            data_str = str(data)
        return (
            "Eres Flash, un analista financiero y de operaciones experto en Rappi.\n"
            "Te doy resultados de una consulta SQL y una pregunta del usuario.\n\n"
            "CONTEXTO DE LOS DATOS:\n"
            "- La columna METRIC indica la métrica. Las columnas L0W_ROLL, L1W_ROLL, etc. "
            "contienen el valor YA CALCULADO de esa métrica para cada semana.\n"
            "- L0W_ROLL = semana actual, L1W_ROLL = semana anterior, L8W_ROLL = hace 8 semanas.\n"
            "- Si la métrica es un ratio o porcentaje (ej. Lead Penetration, Perfect Orders), "
            "el valor en L0W_ROLL YA ES ese ratio en escala 0-1 (ej. 0.73 = 73%). "
            "NO multipliques por 100. Muestra el valor tal como está o conviértelo a % solo si lo indicas explícitamente.\n"
            "- Si hay una columna 'variacion' o similar, es la diferencia ya calculada.\n"
            "- Nunca digas que faltan datos o que necesitas un denominador.\n\n"
            "Analiza los datos como lo haría un analista senior:\n"
            "- Identifica patrones y hallazgos clave\n"
            "- Da contexto de negocio\n"
            "- Sugiere acciones si es relevante\n"
            "Responde en español, claro y accionable.\n\n"
            f"Datos:\n{data_str}\n\n"
            f"Pregunta del usuario: {question}"
        )

    def _build_general_prompt(self, question: str) -> str:
        """
        Construye un prompt conversacional que incluye el historial previo.

        Args:
            question: Pregunta del usuario, puede incluir contexto de conversación
                antepuesto por ConversationMemory.build_context_prompt().

        Returns:
            Cadena de prompt formateada.
        """
        return (
            "Eres Flash, un asistente inteligente experto en operaciones de Rappi.\n"
            "Tu nombre es Flash.\n"
            "Responde usando el contexto de la conversación que te proporciono.\n"
            "Si el usuario hace referencia a algo dicho anteriormente, usa el historial "
            "para responder correctamente.\n"
            "Si te preguntan tu nombre, dices Flash.\n"
            "Responde en español de forma amigable.\n\n"
            f"{question}"
        )

    def generate(self, question: str, data: list[dict]) -> str:
        """
        Genera una respuesta en lenguaje natural.

        Args:
            question: Pregunta del usuario (con contexto del historial opcional).
            data: Resultados de la consulta; lista vacía activa el modo conversacional.

        Returns:
            Cadena de respuesta en español.
        """
        try:
            if data:
                prompt = self._build_analysis_prompt(question, data)
            else:
                prompt = self._build_general_prompt(question)
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt,
            )
            return (response.text or "").strip()
        except Exception as exc:
            logger.error("Generación de respuesta fallida: %s", exc)
            return (
                "Lo siento, ocurrió un error al generar la respuesta. "
                "Por favor intenta de nuevo."
            )
