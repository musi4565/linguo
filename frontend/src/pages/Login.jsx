import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { apiErrorMessage } from "../api/client";
import { useAuth } from "../store/auth";

export default function Login() {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const login = useAuth((s) => s.login);
  const register = useAuth((s) => s.register);
  const navigate = useNavigate();

  const change = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") await login(form.email.trim(), form.password);
      else await register(form.name.trim(), form.email.trim(), form.password);
      navigate("/");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="bg-grid" />
      <div className="blobs">
        <span className="blob blob-1" />
        <span className="blob blob-2" />
        <span className="blob blob-3" />
      </div>

      <form className="auth-card glass" onSubmit={submit}>
        <Link to="/onboarding" className="logo auth-logo">
          LINGUO
        </Link>
        <h2>{mode === "login" ? "Hisobingizga kirish" : "Ro'yxatdan o'tish"}</h2>
        <p className="auth-sub">
          {mode === "login"
            ? "O'rganishni davom ettiring"
            : "Bir daqiqada hisob yarating"}
        </p>

        {mode === "register" && (
          <label className="field">
            Ism
            <input
              type="text"
              value={form.name}
              onChange={change("name")}
              placeholder="Ismingiz"
              required
              minLength={2}
            />
          </label>
        )}
        <label className="field">
          Email
          <input
            type="email"
            value={form.email}
            onChange={change("email")}
            placeholder="siz@example.com"
            required
          />
        </label>
        <label className="field">
          Parol
          <input
            type="password"
            value={form.password}
            onChange={change("password")}
            placeholder="Kamida 8 belgi"
            required
            minLength={8}
          />
        </label>

        {error && <div className="form-error">{error}</div>}

        <button className="btn-primary btn-block" disabled={busy}>
          {busy ? "Yuklanmoqda..." : mode === "login" ? "Kirish" : "Ro'yxatdan o'tish"}
        </button>

        <p className="auth-switch">
          {mode === "login" ? (
            <>
              Hisobingiz yo'qmi?{" "}
              <a href="#register" onClick={(e) => { e.preventDefault(); setMode("register"); setError(""); }}>
                Ro'yxatdan o'tish
              </a>
            </>
          ) : (
            <>
              Allaqachon hisobingiz bormi?{" "}
              <a href="#login" onClick={(e) => { e.preventDefault(); setMode("login"); setError(""); }}>
                Kirish
              </a>
            </>
          )}
        </p>
      </form>
    </div>
  );
}
