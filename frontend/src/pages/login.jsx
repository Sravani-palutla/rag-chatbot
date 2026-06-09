import { useState } from "react";
import { useNavigate } from "react-router-dom";
import backend from "../services/backend";

function Login() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isSignup, setIsSignup] = useState(false);

  const handleSubmit = async () => {
    try {
      const formData = new FormData();

      formData.append("username", username);
      formData.append("password", password);

      if (isSignup) {
        await backend.post("/signup", formData);

        setMessage("Account created successfully. Please login.");
        setIsSignup(false);
        return;
      }

      const response = await backend.post("/login", formData);

      localStorage.setItem("token", response.data.access_token);
      localStorage.setItem("username", response.data.username);

      navigate("/chat");

    } catch (error) {
      if (isSignup) {
        setMessage("Signup failed");
      } else {
        setMessage("Invalid username or password");
      }
    }
  };

  return (
    <div className="login-page">

      <div className="login-screen">

        <div className="score-row">
          <span>USER LOGIN</span>
          <span>DOCUMENT INTELLIGENCE SYSTEM</span>
          <span>09 JUN 2026</span>
        </div>

        <h1 className="arcade-title">
          DOCUMENT QUEST
        </h1>

        <div className="menu-text">
          <p
            onClick={() => setIsSignup(false)}
            style={{
              cursor: "pointer",
              color: !isSignup ? "#ffffff" : "#999"
            }}
          >
            {">"} LOGIN
          </p>

          <p
            onClick={() => setIsSignup(true)}
            style={{
              cursor: "pointer",
              color: isSignup ? "#ffffff" : "#999"
            }}
          >
            {">"} SIGN UP
          </p>
        </div>

        <div className="login-form">

          <input
            type="text"
            placeholder="USERNAME"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            placeholder="PASSWORD"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button onClick={handleSubmit}>
            {isSignup ? "CREATE ACCOUNT" : "ENTER"}
          </button>

          <p className="error-text">
            {message}
          </p>

        </div>

      </div>

    </div>
  );
}

export default Login;