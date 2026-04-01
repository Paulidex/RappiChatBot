import { ENDPOINTS } from "../constants/endpoints";

export async function askQuestion(question, signal) {
  const response = await fetch(ENDPOINTS.ask, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pregunta: question }),
    signal: signal,
  });

  if (!response.ok) {
    throw new Error("HTTP error! status: " + response.status);
  }

  return response.json();
}

export async function stopGeneration() {
  return fetch(ENDPOINTS.stop, { method: "POST" });
}
