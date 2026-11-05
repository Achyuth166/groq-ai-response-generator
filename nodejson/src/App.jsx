
import { useState } from "react";

function App() {
  const [message, setMessage] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const startNewChat = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat/new", {
        method: "POST",
      });

      if (!res.ok) throw new Error("Could not create chat");

      const data = await res.json();

      setSessionId(data.session_id);
      setChatHistory([]);
      setResponse("New chat created successfully!");
    } catch (error) {
      setResponse(error.message);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || !sessionId) {
      setResponse("Create a new chat first and enter a message.");
      return;
    }

    setLoading(true);
    setResponse("");

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId,
        }),
      });

      if (!res.ok) throw new Error("Backend request failed");

      const data = await res.json();

      setChatHistory(data.chat_history);
      setMessage("");
    } catch (error) {
      setResponse(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h1>Groq AI Chat Application</h1>

      <button onClick={startNewChat}>
        New Chat
      </button>

      <p>Session ID: {sessionId || "No session created"}</p>

      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Enter your message"
      />

      <button onClick={sendMessage} disabled={loading}>
        {loading ? "Sending..." : "Send Message"}
      </button>

      <h3>Conversation History</h3>

      {chatHistory.map((chat, index) => (
        <div key={index}>
          <strong>
            {chat.role === "user" ? "You" : "AI"}:
          </strong>
          <p>{chat.content}</p>
        </div>
      ))}

      {response && <p>{response}</p>}
    </div>
  );
}

export default App;
