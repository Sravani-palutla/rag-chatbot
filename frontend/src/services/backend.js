import axios from "axios";

const backend = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

backend.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default backend;