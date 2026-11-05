const API_URL = "http://127.0.0.1:8000";

export async function sendMessage(message, sessionId) {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error("Backend connection failed");
  }

  return await response.json();
}