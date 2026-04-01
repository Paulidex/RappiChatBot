const API_BASE_URL = "http://127.0.0.1:8000";

export const ENDPOINTS = {
  ask: `${API_BASE_URL}/preguntar`,
  stop: `${API_BASE_URL}/detener`,
  generatePdf: `${API_BASE_URL}/generar_pdf`,
  insights: `${API_BASE_URL}/insights`,
  generateReport: `${API_BASE_URL}/generar_reporte`,
};
