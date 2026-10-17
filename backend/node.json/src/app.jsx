
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!message.trim()) {
      setError("Please enter a message.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/respond",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message }),
          signal: AbortSignal.timeout(15000),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail
              .map((item) => item.msg)
              .join(", ")
          : typeof data.detail === "string"
            ? data.detail
            : "Request failed. Check your backend.";

        throw new Error(
          `HTTP ${response.status}: ${detail}`
        );
      }

      setResult(data);
    } catch (err) {
      if (err.name === "TimeoutError") {
        setError("Request timed out. Please try again.");
      } else if (err.name === "TypeError") {
        setError(
          "Cannot connect to the backend. Make sure the server is running."
        );
      } else {
        setError(
          err.message || "Something went wrong. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1>AI Response Generator</h1>
      <p>Enter a message to generate an AI response.</p>

      <form onSubmit={handleSubmit}>
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Type your message..."
          rows={4}
          disabled={loading}
        />

        <button type="submit" disabled={loading}>
          {loading ? "Generating..." : "Generate Response"}
        </button>
      </form>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {result && (
        <section className="result">
          <h2>Detected Intent</h2>
          <p>{result.intent}</p>

          <h2>Summary</h2>
          <p>{result.summary}</p>

          <h2>AI Response</h2>
          <ReactMarkdown>
            {result.answer_markdown}
          </ReactMarkdown>
        </section>
      )}
    </main>
  );
}

export default App;

