const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

export const ENDPOINTS = {
  chat: `${API_BASE_URL}/chat`,
  chatExportPdf: (sessionId) => `${API_BASE_URL}/chat/${sessionId}/export-pdf`,
  insights: `${API_BASE_URL}/insights/initial`,
  reportPdf: `${API_BASE_URL}/insights/report-pdf`,
};
