import InsightCard from "./InsightCard";
import { useInsights } from "../../hooks/useInsights";
import { generateReportPdf } from "../../api/insights";
import spinnerSvg from "../../assets/spinner.svg?raw";
import refreshSvg from "../../assets/refresh.svg?raw";
import barChartSvg from "../../assets/bar-chart.svg?raw";
import text from "../../constants/text.json";

function InsightPanelHeader({ isLoading, onRefresh, onGenerateReport }) {
  return (
    <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-3 sm:mb-4 gap-3 sm:gap-4">
      <hgroup>
        <h2 className="text-xl sm:text-2xl font-bold text-gray-800">
          {text.insights.title}
        </h2>
        <p className="text-gray-600 text-xs sm:text-sm mt-1">
          {text.insights.subtitle}
        </p>
      </hgroup>

      <menu className="flex items-stretch gap-2 w-full sm:w-auto flex-wrap sm:flex-nowrap list-none m-0 p-0">
        <li className="flex">
          <button
            onClick={onGenerateReport}
            className="w-full px-4 sm:px-6 py-2 sm:py-3 rounded-2xl bg-linear-to-r from-[#f5bf7b] to-[#f39c36] hover:from-[#f39c36] hover:to-[#f5bf7b] transition-all duration-300 flex items-center justify-center gap-2 text-sm sm:text-base"
          >
            <span className="text-black font-bold whitespace-nowrap">
              {text.insights.generateReportButton}
            </span>
          </button>
        </li>

        <li className="flex">
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="w-full px-4 sm:px-6 py-2 sm:py-3 rounded-2xl bg-linear-to-r from-[#fd6331] to-[#ff3e53] text-white hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center gap-2 text-sm sm:text-base"
          >
            {isLoading ? (
              <>
                <span
                  className="animate-spin h-5 w-5 inline-block"
                  dangerouslySetInnerHTML={{ __html: spinnerSvg }}
                />
                {text.insights.generatingButton}
              </>
            ) : (
              <>
                <span
                  className="h-5 w-5 inline-block"
                  dangerouslySetInnerHTML={{ __html: refreshSvg }}
                />
                {text.insights.refreshButton}
              </>
            )}
          </button>
        </li>
      </menu>
    </header>
  );
}

function LoadingState() {
  return (
    <p role="status" className="flex-1 flex flex-col items-center justify-center text-center">
      <span
        className="animate-spin h-12 w-12 inline-block text-[#fd6331] mb-4"
        dangerouslySetInnerHTML={{ __html: spinnerSvg }}
      />
      <span className="text-gray-600 text-lg">{text.insights.loadingTitle}</span>
      <span className="text-gray-500 text-sm mt-2">{text.insights.loadingSubtitle}</span>
    </p>
  );
}

function EmptyState() {
  return (
    <p role="status" className="flex-1 flex flex-col items-center justify-center text-center">
      <span
        className="h-16 w-16 inline-block text-gray-300 mb-4"
        dangerouslySetInnerHTML={{ __html: barChartSvg }}
      />
      <span className="text-gray-600 text-lg">{text.insights.emptyTitle}</span>
      <span className="text-gray-500 text-sm mt-2">{text.insights.emptySubtitle}</span>
    </p>
  );
}

function ErrorBanner({ message }) {
  return (
    <p role="alert" className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-red-600">
      ⚠️ {message}
    </p>
  );
}

function InsightGrid({ insights }) {
  return (
    <ul className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4 md:gap-6 mt-4 sm:mt-6 list-none m-0 p-0">
      {insights.map((insight) => (
        <li key={insight.id}>
          <InsightCard
            title={insight.title}
            description={insight.description}
            chartUrl={insight.chartUrl}
            error={insight.error}
          />
        </li>
      ))}
    </ul>
  );
}

export default function InsightPanel({ visible }) {
  const { insights, isLoading, error, loadInsights } = useInsights(visible);

  async function handleGenerateReport() {
    await generateReportPdf(insights);
  }

  return (
    <section
      className={`w-full h-full bg-white rounded-2xl p-3 sm:p-4 md:p-6 shadow-sm flex flex-col overflow-y-auto box-border ${
        visible ? "block" : "hidden"
      }`}
    >
      <InsightPanelHeader
        isLoading={isLoading}
        onRefresh={loadInsights}
        onGenerateReport={handleGenerateReport}
      />

      {error && <ErrorBanner message={error} />}

      {isLoading && insights.length === 0 ? (
        <LoadingState />
      ) : insights.length > 0 ? (
        <InsightGrid insights={insights} />
      ) : (
        <EmptyState />
      )}
    </section>
  );
}
