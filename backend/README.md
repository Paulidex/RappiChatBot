# Flash — Sistema de Análisis Inteligente para Operaciones Rappi

**Flash** es el bot de análisis inteligente de Rappi. Responde preguntas en lenguaje natural sobre métricas operacionales, genera gráficas, detecta anomalías y produce reportes ejecutivos en PDF.

---

## Arquitectura

```
backend/
├── app/
│   ├── config/          # Settings (Singleton)
│   ├── entities/        # Dataclasses de dominio
│   ├── models/          # Request/Response Pydantic
│   ├── interfaces/      # ABCs (contratos)
│   ├── repositories/    # SQLite (Repository pattern)
│   ├── database/        # SqliteExecutor (validación SQL)
│   ├── llm/             # Gemini: clasificador, SQL, respuesta, PDF
│   ├── generators/      # Matplotlib + fpdf2
│   ├── analyzers/       # Strategy: anomalías, tendencias, benchmarking, correlación
│   ├── services/        # ChatService, InsightService, ConversationMemory
│   └── routers/         # FastAPI routers (chat, insights, health)
├── tests/
├── data/                # Excel fuente + SQLite generado
├── .env
├── .env.example
└── requirements.txt
```

### Patrones utilizados

| Patrón     | Uso                                                                            |
| ---------- | ------------------------------------------------------------------------------ |
| Singleton  | `Settings`                                                                     |
| Repository | `SqliteMetricRepository`, `SqliteOrderRepository`                              |
| Strategy   | `AnomalyAnalyzer`, `TrendAnalyzer`, `BenchmarkAnalyzer`, `CorrelationAnalyzer` |
| Factory    | `InsightAnalyzerFactory`                                                       |

---

## Instalación

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

---

## Configuración

Copia `.env.example` a `.env` y completa los valores:

El archivo Excel debe tener dos hojas:

- `RAW_INPUT_METRICS` — métricas operacionales por zona
- `RAW_ORDERS` — volumen de órdenes por zona

---

## Ejecución

```bash
cd backend
python -m app.main
```

La API queda disponible en `http://localhost:8000`.  
Documentación interactiva: `http://localhost:8000/docs`

---

## Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## Endpoints

### Chat (Flash)

| Método | Ruta                                   | Descripción                 |
| ------ | -------------------------------------- | --------------------------- |
| POST   | `/api/v1/chat`                         | Enviar mensaje a Flash      |
| GET    | `/api/v1/chat/{session_id}/history`    | Historial de conversación   |
| DELETE | `/api/v1/chat/{session_id}`            | Eliminar sesión             |
| GET    | `/api/v1/chat/{session_id}/export-pdf` | Exportar historial como PDF |

### Insights

| Método | Ruta                          | Descripción                          |
| ------ | ----------------------------- | ------------------------------------ |
| GET    | `/api/v1/insights/initial`    | 10 insights precargados con gráficas |
| POST   | `/api/v1/insights/report-pdf` | Generar reporte ejecutivo PDF        |
| GET    | `/api/v1/insights/categories` | Categorías de análisis disponibles   |

### Health

| Método | Ruta             | Descripción         |
| ------ | ---------------- | ------------------- |
| GET    | `/api/v1/health` | Estado del servicio |

---

## Módulos principales

### Módulo 1 — Bot Conversacional (Flash)

Flash clasifica cada mensaje en tres ramas:

- **chart** → genera SQL + ejecuta + análisis textual + gráfica Matplotlib
- **query** → genera SQL + ejecuta + análisis textual
- **general** → usa historial de conversación como contexto para el LLM

### Módulo 2 — Insights Automáticos

Al cargar la app ejecuta 10 consultas SQL predefinidas y genera gráficas.  
El botón "Generar Reporte" produce un PDF ejecutivo con narrativa de Gemini + gráficas incrustadas.

---
