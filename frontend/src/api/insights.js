import { ENDPOINTS } from "../constants/endpoints";

function transformInsight(rawInsight) {
  return {
    id: rawInsight.id,
    title: rawInsight.titulo,
    description: rawInsight.descripcion,
    chartUrl: rawInsight.grafica,
    error: rawInsight.error,
  };
}

export async function fetchInsights() {
  const response = await fetch(ENDPOINTS.insights, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });

  const data = await response.json();

  if (data.error) {
    throw new Error(data.error);
  }

  const rawInsights = data.insights || [];
  const transformedInsights = rawInsights.map(transformInsight);

  return transformedInsights;
}
