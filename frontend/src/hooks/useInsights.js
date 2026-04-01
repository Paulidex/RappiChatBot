import { useState, useEffect } from "react";
import { fetchInsights } from "../api/insights";
import text from "../constants/text.json";

export function useInsights(isVisible) {
  const [insights, setInsights] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isVisible && insights.length === 0) {
      loadInsights();
    }
  }, [isVisible, insights.length]);

  async function loadInsights() {
    setIsLoading(true);
    setError(null);

    try {
      const insightList = await fetchInsights();
      setInsights(insightList);
    } catch (err) {
      setError(text.insights.loadError + " " + err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return { insights, isLoading, error, loadInsights };
}
