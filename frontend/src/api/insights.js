import { ENDPOINTS } from "../constants/endpoints";

export async function fetchInsights() {
  const response = await fetch(ENDPOINTS.insights);

  if (!response.ok) {
    throw new Error("HTTP error! status: " + response.status);
  }

  const data = await response.json();
  const insightsData = data.insights_data || [];
  const charts = data.chart_base64_list || [];

  return insightsData.map((insight, index) => ({
    id: index,
    title: insight.title,
    description: insight.description,
    category: insight.category,
    severity: insight.severity,
    recommendation: insight.recommendation,
    chartUrl: charts[index] ? `data:image/png;base64,${charts[index]}` : null,
    error: null,
  }));
}

export async function generateReportPdf(insights) {
  const response = await fetch(ENDPOINTS.reportPdf, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ insights }),
  });

  if (!response.ok) {
    throw new Error("HTTP error! status: " + response.status);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  window.open(url, "_blank");
  setTimeout(() => URL.revokeObjectURL(url), 10000);
}
