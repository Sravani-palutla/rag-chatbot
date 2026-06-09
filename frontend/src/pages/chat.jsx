import { useEffect, useState } from "react";
import backend from "../services/backend";

function Chat() {
  const username = localStorage.getItem("username");

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadedFileName, setUploadedFileName] = useState("");
  const [uploadMessage, setUploadMessage] = useState("");

  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [suggestions, setSuggestions] = useState([
    "What are the key points?",
    "Explain this simply.",
    "How is this used in the project?",
  ]);

  const loadHistory = async () => {
    try {
      await backend.get("/history");
    } catch (error) {
      console.log("History loading failed", error);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage("Please select a file first.");
      return;
    }

    try {
      setUploadMessage("Uploading...");

      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await backend.post("/upload", formData);

      setUploadedFileName(response.data.file_name);
      setUploadMessage("Uploaded successfully.");

      await loadHistory();
    } catch (error) {
      console.log(error);
      setUploadMessage("Upload failed.");
    }
  };

  const handleSend = async () => {
    if (!query.trim()) return;

    if (!uploadedFileName) {
      setMessages((prev) => [
        ...prev,
        { type: "bot", text: "Please upload a document first." },
      ]);
      return;
    }

    const userQuestion = query;

    setMessages((prev) => [
      ...prev,
      { type: "user", text: userQuestion },
    ]);

    setQuery("");

    try {
      const formData = new FormData();
      formData.append("file_name", uploadedFileName);
      formData.append("query", userQuestion);

      const response = await backend.post("/chat", formData);

      setMessages((prev) => [
        ...prev,
        { type: "bot", text: response.data.answer },
      ]);

      setSuggestions(response.data.suggested_questions || []);

      await loadHistory();
    } catch (error) {
      console.log(error);

      setMessages((prev) => [
        ...prev,
        { type: "bot", text: "Something went wrong while getting the answer." },
      ]);
    }
  };

  return (
    <div className="chat-page">
      <aside className="side-panel panel">
        <h2>Document Quest</h2>
        <p className="user-name">Logged in as {username}</p>

        <div className="section">
          <h3>Upload Document</h3>

          <input
            type="file"
            accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
            onChange={(e) => setSelectedFile(e.target.files[0])}
          />

          <button onClick={handleUpload}>Upload</button>

          <p className="empty-text">
            {uploadedFileName
              ? `Current file: ${uploadedFileName}`
              : "No file uploaded."}
          </p>

          <p className="empty-text">{uploadMessage}</p>
        </div>

        <div className="section">
          <h3>Suggested Questions</h3>

          {suggestions.map((question, index) => (
            <button
              key={index}
              className="suggestion-btn"
              onClick={() => setQuery(question)}
            >
              {question}
            </button>
          ))}
        </div>
      </aside>

      <main className="chat-panel panel">
        <div className="chat-header">
          <h1>Document Intelligence Chat</h1>
          <p>Upload a document and ask questions from it.</p>
        </div>

        <div className="messages-box">
          {messages.length === 0 ? (
            <p className="empty-text">
              Your answers will appear here.
            </p>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={
                  message.type === "user"
                    ? "message user-message"
                    : "message bot-message"
                }
              >
                {message.text}
              </div>
            ))
          )}
        </div>

        <div className="input-row">
          <input
            type="text"
            placeholder="Enter your question..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          <button onClick={handleSend}>Send</button>
        </div>
      </main>
    </div>
  );
}

export default Chat;