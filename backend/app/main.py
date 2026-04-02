import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.logging_config import setup_logging
from app.config.settings import Settings

setup_logging()
from app.database.sqlite_executor import SqliteExecutor
from app.repositories.sqlite_metric_repository import SqliteMetricRepository
from app.repositories.sqlite_order_repository import SqliteOrderRepository
from app.llm.llm_intent_classifier import LlmIntentClassifier
from app.llm.llm_sql_generator import LlmSqlGenerator
from app.llm.llm_response_generator import LlmResponseGenerator
from app.llm.llm_report_pdf_generator import LlmReportPdfGenerator
from app.generators.matplotlib_chart_generator import MatplotlibChartGenerator
from app.generators.chat_history_pdf_generator import ChatHistoryPdfGenerator
from app.services.conversation_memory import ConversationMemory
from app.services.chat_service import ChatService
from app.services.insight_service import InsightService
from app.analyzers.insight_analyzer_factory import InsightAnalyzerFactory
from app.routers.chat_router import ChatRouter
from app.routers.insight_router import InsightRouter
from app.routers.health_router import HealthRouter


class Main():
    def __init__(self):
        self._app = FastAPI(
            title="Rappi Insights API",
            version="1.0.0",
            description="Sistema de Análisis Inteligente para Operaciones Rappi"
        )
        self._settings = Settings.get_instance()
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._setup()

    def _setup(self) -> None:
        self._init_database()
        self._init_repositories()
        self._init_llm()
        self._init_generators()
        self._init_services()
        self._init_routers()

    def _init_database(self) -> None:
        self._sql_executor = SqliteExecutor(
            connection_path=self._settings.db_path
        )

    def _init_repositories(self) -> None:
        self._metric_repo = SqliteMetricRepository(
            db_path=self._settings.db_path,
            csv_path=self._settings.metric_file_path
        )
        self._order_repo = SqliteOrderRepository(
            db_path=self._settings.db_path,
            csv_path=self._settings.order_file_path
        )

    def _init_llm(self) -> None:
        self._intent_classifier = LlmIntentClassifier(
            api_key=self._settings.llm_api_key,
            model_name=self._settings.llm_model_name
        )
        self._sql_generator = LlmSqlGenerator(
            api_key=self._settings.llm_api_key,
            model_name=self._settings.llm_model_name,
            db_schema=self._sql_executor.get_schema()
        )
        self._response_generator = LlmResponseGenerator(
            api_key=self._settings.llm_api_key,
            model_name=self._settings.llm_model_name
        )
        self._report_pdf_generator = LlmReportPdfGenerator(
            api_key=self._settings.llm_api_key,
            model_name=self._settings.llm_model_name
        )

    def _init_generators(self) -> None:
        self._chart_generator = MatplotlibChartGenerator()
        self._history_pdf_generator = ChatHistoryPdfGenerator()
        self._analyzers = InsightAnalyzerFactory.create_all_analyzers()
        self._memory = ConversationMemory(max_history=20)

    def _init_services(self) -> None:
        self._chat_service = ChatService(
            classifier=self._intent_classifier,
            sql_generator=self._sql_generator,
            sql_executor=self._sql_executor,
            response_generator=self._response_generator,
            chart_generator=self._chart_generator,
            memory=self._memory,
            history_pdf_gen=self._history_pdf_generator
        )
        self._insight_service = InsightService(
            metric_repo=self._metric_repo,
            order_repo=self._order_repo,
            response_generator=self._response_generator,
            chart_generator=self._chart_generator,
            report_pdf_gen=self._report_pdf_generator,
            analyzers=self._analyzers
        )

    def _init_routers(self) -> None:
        chat_router = ChatRouter(chat_service=self._chat_service)
        insight_router = InsightRouter(insight_service=self._insight_service)
        health_router = HealthRouter()

        self._app.include_router(chat_router.router, prefix="/api/v1")
        self._app.include_router(insight_router.router, prefix="/api/v1")
        self._app.include_router(health_router.router, prefix="/api/v1")

    def get_app(self) -> FastAPI:
        return self._app


if __name__ == "__main__":
    main = Main()
    app = main.get_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)