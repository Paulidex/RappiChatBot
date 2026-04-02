# app/llm/llm_sql_generator.py
"""Generador de SQL basado en LLM para consultas de datos de Flash (backend Gemini)."""

import logging
import re
from google import genai
from app.interfaces.i_sql_generator import ISqlGenerator
from app.entities.query_intent import QueryIntent

logger = logging.getLogger(__name__)



class LlmSqlGenerator(ISqlGenerator):
    """
    Genera sentencias SELECT de SQLite a partir de intenciones de usuario clasificadas
    utilizando Google Gemini.

    El esquema de la base de datos se inyecta en el constructor para que el modelo
    siempre conozca los nombres exactos de las columnas disponibles.
    """

    def __init__(self, api_key: str, model_name: str, db_schema: str = "") -> None:
        """
        Inicializa el generador de SQL.

        Args:
            api_key: Clave API de Gemini.
            model_name: Identificador del modelo Gemini.
            db_schema: DDL CREATE TABLE de la base de datos (opcional).
        """
        self._api_key = api_key
        self._model_name = model_name
        self._db_schema = db_schema
        self._client = genai.Client(api_key=api_key)

    def _build_sql_prompt(self, intent: QueryIntent) -> str:
        """
        Construye el prompt que le pide a Gemini producir una consulta SQL.

        Args:
            intent: Intención de usuario clasificada con filtros extraídos.

        Returns:
            Cadena de prompt formateada.
        """
        filters_str = (
            "\n".join(f"  - {k}: {v}" for k, v in intent.extracted_filters.items() if v)
            or "  (ninguno)"
        )
        return (
            "Eres un experto en SQLite. Genera SOLO SQL SELECT válido para SQLite.\n"
            "Sin markdown, sin explicación, sin comentarios. Solo el SQL.\n\n"
            "REGLAS OBLIGATORIAS para el SELECT:\n"
            "  1. Siempre incluye COUNTRY, CITY, ZONE en el SELECT.\n"
            "  2. Siempre incluye las columnas numéricas relevantes (ej. L0W_ROLL, L1W_ROLL, o la diferencia calculada).\n"
            "  3. Nunca selecciones SOLO columnas de identificación sin valores numéricos.\n"
            "  4. Si calculas una diferencia o variación, inclúyela como columna con alias (ej. L0W_ROLL - L1W_ROLL AS variacion).\n"
            "  5. Usa LIMIT 20 si no se especifica un top N.\n"
            "  6. Usa la tabla 'metrics' para métricas operacionales. Usa la tabla 'orders' solo para volumen de órdenes.\n"
            "  7. El valor del campo METRIC debe copiarse EXACTAMENTE del diccionario de métricas. "
            "Nunca añadas ni quites caracteres (%, #, espacios, etc.). "
            "Ejemplo: si el usuario dice '% Lead Penetration', el valor correcto en el WHERE es 'Lead Penetration'.\n\n"
            f"Schema real de la base de datos (tipos de columna):\n{self._db_schema}\n\n"
            "--- DATASET 1: tabla 'metrics' (métricas operacionales por zona) ---\n"
            "Columnas:\n"
            "  COUNTRY          string  Código de país (AR, BR, CL, CO, CR, EC, MX, PE, UY)\n"
            "  CITY             string  Nombre de la ciudad\n"
            "  ZONE             string  Zona operacional o barrio\n"
            "  ZONE_TYPE        string  Segmentación por riqueza: 'Wealthy' / 'Non Wealthy'\n"
            "  ZONE_PRIORITIZATION string Priorización estratégica: 'High Priority' / 'Prioritized' / 'Not Prioritized'\n"
            "  METRIC           string  Nombre exacto de la métrica (ver diccionario abajo)\n"
            "  L8W_ROLL … L0W_ROLL float Valor de la métrica por semana: L0W_ROLL=semana actual, L1W_ROLL=semana anterior, …, L8W_ROLL=hace 8 semanas\n\n"
            "--- DATASET 2: tabla 'orders' (volumen de órdenes por zona) ---\n"
            "Columnas:\n"
            "  COUNTRY, CITY, ZONE  Identificadores geográficos\n"
            "  METRIC           string  Siempre 'Orders'\n"
            "  L8W … L0W        int     Número de órdenes por semana: L0W=semana actual, …, L8W=hace 8 semanas\n\n"
            "--- DICCIONARIO DE MÉTRICAS (valores EXACTOS del campo METRIC en tabla metrics) ---\n"
            "  '% PRO Users Who Breakeven'                → usuarios Pro cuyo valor generado cubrió el costo de membresía / total usuarios Pro\n"
            "  '% Restaurants Sessions With Optimal Assortment' → sesiones con mínimo 40 restaurantes / total sesiones\n"
            "  'Gross Profit UE'                          → margen bruto de ganancia / total órdenes\n"
            "  'Lead Penetration'                         → tiendas habilitadas en Rappi / (leads + habilitadas + salidas)\n"
            "  'MLTV Top Verticals Adoption'              → usuarios con órdenes en múltiples verticales / total usuarios\n"
            "  'Non-Pro PTC > OP'                         → conversión de usuarios No Pro de Proceed to Checkout a Order Placed\n"
            "  'Perfect Orders'                           → órdenes sin cancelaciones, defectos ni demora / total órdenes\n"
            "  'Pro Adoption (Last Week Status)'           → usuarios suscripción Pro / total usuarios Rappi\n"
            "  'Restaurants Markdowns / GMV'              → descuentos totales en restaurantes / GMV restaurantes\n"
            "  'Restaurants SS > ATC CVR'                 → conversión de Select Store a Add to Cart en restaurantes\n"
            "  'Restaurants SST > SS CVR'                 → usuarios que seleccionan una tienda tras entrar a restaurantes\n"
            "  'Retail SST > SS CVR'                      → usuarios que seleccionan una tienda tras entrar a supermercados\n"
            "  'Turbo Adoption'                           → usuarios que compran en Turbo / total usuarios con Turbo disponible\n\n"
            f"Pregunta del usuario: {intent.original_question}\n\n"
            f"Filtros extraídos:\n{filters_str}\n\n"
            "Genera únicamente el SQL SELECT:"
        )

    def generate_sql(self, intent: QueryIntent) -> str:
        """
        Genera una sentencia SQL SELECT a partir de la intención dada.

        En caso de error retorna una consulta segura por defecto.

        Args:
            intent: Intención de consulta clasificada con filtros extraídos.

        Returns:
            Cadena con una sentencia SELECT válida de SQLite.
        """
        try:
            prompt = self._build_sql_prompt(intent)
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt,
            )
            raw = (response.text or "").strip()
            raw = re.sub(r"```(?:sql)?", "", raw, flags=re.IGNORECASE).strip("` \n")
            if not raw.upper().startswith("SELECT"):
                logger.warning("Gemini retornó SQL inválido: %s", raw)
                raise ValueError("No se pudo generar una consulta SQL válida para tu pregunta.")
            return raw
        except ValueError:
            raise
        except Exception as exc:
            logger.error("Generación de SQL fallida: %s", exc)
            raise RuntimeError("Error al generar la consulta. Por favor intenta de nuevo.") from exc
