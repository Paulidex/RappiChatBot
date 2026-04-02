import { ENDPOINTS } from "../constants/endpoints";

export async function sendMessage(sessionId, userMessage, signal) {
  const response = await fetch(ENDPOINTS.chat, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, user_message: userMessage }),
    signal,
  });

  if (!response.ok) {
    throw new Error("HTTP error! status: " + response.status);
  }

  return response.json();
}

export function exportHistoryPdf(sessionId) {
  window.open(ENDPOINTS.chatExportPdf(sessionId), "_blank");
}
