import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api, apiErrorMessage } from "../api/client";
import Modal from "../components/Modal.jsx";
import { useAuth } from "../store/auth";

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalSection, setModalSection] = useState(null);
  const [nameDraft, setNameDraft] = useState("");
  const [pwForm, setPwForm] = useState({ old_password: "", new_password: "" });
  const [msg, setMsg] = useState("");
  const logout = useAuth((s) => s.logout);
  const navigate = useNavigate();

  function load() {
    api
      .get("/profile/")
      .then((r) => setProfile(r.data))
      .catch(() => setProfile({ user: null }));
  }
  useEffect(load, []);

  if (!profile) return <div className="loading">Yuklanmoqda...</div>;

  const user = profile.user || {};
  const initials = user.name
    ? user.name.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase()
    : "?";

  async function saveName() {
    try {
      await api.patch("/profile/", { name: nameDraft });
      setMsg("Ism saqlandi ✓");
      setModalSection(null);
      load();
      useAuth.getState().fetchUser().catch(() => {});
    } catch (e) {
      setMsg(apiErrorMessage(e));
    }
    setTimeout(() => setMsg(""), 2500);
  }

  async function savePassword() {
    try {
      await api.patch("/profile/password/", pwForm);
      setMsg("Parol o'zgartirildi ✓");
      setPwForm({ old_password: "", new_password: "" });
      setModalSection(null);
    } catch (e) {
      setMsg(apiErrorMessage(e));
    }
    setTimeout(() => setMsg(""), 3000);
  }

  function doLogout() {
    logout();
    navigate("/login");
  }

  async function connectTelegram() {
    try {
      const { data } = await api.get("/auth/telegram/connect-url/");
      if (data.connected) {
        setMsg("Bot allaqachon ulangan ✓");
        setTimeout(() => setMsg(""), 2500);
        return;
      }
      window.open(data.url, "_blank", "noopener");
    } catch (e) {
      setMsg(apiErrorMessage(e));
      setTimeout(() => setMsg(""), 2500);
    }
  }

  const month = profile.month || {};

  return (
    <div className="profile-page">
      <section className="profile-card glass">
        <span className="avatar big">{initials}</span>
        <div className="profile-id">
          <h2>{user.name}</h2>
          <span className="muted">{user.email}</span>
        </div>
        <span className={`streak-chip${profile.streak ? "" : " inactive"}`}>
          {profile.streak > 0 ? `🔥 ${profile.streak} kunlik seriya` : "📈 Hali seriya boshlanmagan"}
        </span>
        {profile.telegram_connected ? (
          <a
            href="https://t.me/linguo_uz_bot"
            target="_blank"
            rel="noopener noreferrer"
            className="tg-connect done"
            title="Botni ochish"
          >
            📲 Bot ulangan
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{marginLeft: 4}}>
              <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6" />
              <polyline points="15 3 21 3 21 9" />
              <line x1="10" y1="14" x2="21" y2="3" />
            </svg>
          </a>
        ) : (
          <button
            className="tg-connect"
            onClick={connectTelegram}
            title="LINGUO Telegram boti"
          >
            📲 Telegram botga ulanish
          </button>
        )}
        <button
          className="icon-btn gear"
          title="Sozlamalar"
          onClick={() => {
            setModalOpen(true);
            setModalSection(null);
          }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" />
          </svg>
        </button>
      </section>

      <div className="profile-panels">
        <section className="panel glass">
          <h3>Bu oydagi natijalar</h3>
          <div className="mini-stats">
            <MiniStat value={month.minutes_spent ?? 0} label="daqiqa" />
            <MiniStat value={month.words_saved ?? 0} label="so'z" />
            <MiniStat value={month.lessons_completed ?? 0} label="dars" />
            <MiniStat value={month.active_days ?? 0} label="faol kun" />
          </div>
        </section>

        <section className="panel glass">
          <h3>Yutuqlar</h3>
          <div className="badges">
            {(profile.achievements || []).map((a) => (
              <div key={a.code} className={`badge${a.earned ? " earned" : ""}`} title={a.condition_description}>
                <span className="badge-icon">{a.icon}</span>
                <span className="badge-title">{a.title}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <h3 className="modal-title">Sozlamalar</h3>
        {msg && <div className="save-toast inline">{msg}</div>}

        <button className="setting-row" onClick={() => setModalSection(modalSection === "info" ? null : "info")}>
          👤 Shaxsiy ma'lumotlar
        </button>
        {modalSection === "info" && (
          <div className="setting-body">
            <label className="field">
              Ism
              <input value={nameDraft} onChange={(e) => setNameDraft(e.target.value)} placeholder={user.name} />
            </label>
            <button className="btn-primary btn-sm" onClick={saveName}>Saqlash</button>
          </div>
        )}

        <button className="setting-row" onClick={() => setModalSection(modalSection === "pass" ? null : "pass")}>
          🔒 Parol
        </button>
        {modalSection === "pass" && (
          <div className="setting-body">
            <label className="field">
              Eski parol
              <input type="password" value={pwForm.old_password}
                onChange={(e) => setPwForm({ ...pwForm, old_password: e.target.value })} />
            </label>
            <label className="field">
              Yangi parol
              <input type="password" value={pwForm.new_password}
                onChange={(e) => setPwForm({ ...pwForm, new_password: e.target.value })} />
            </label>
            <button className="btn-primary btn-sm" onClick={savePassword}>O'zgartirish</button>
          </div>
        )}

        <button className="setting-row muted-row" disabled>
          🔔 Bildirishnomalar <em className="soon">tez orada</em>
        </button>
        <button className="setting-row muted-row" disabled>
          🌐 Interfeys tili <em className="soon">tez orada</em>
        </button>

        <button className="setting-row danger-row" onClick={doLogout}>
          🚪 Tizimdan chiqish
        </button>
      </Modal>
    </div>
  );
}

function MiniStat({ value, label }) {
  return (
    <div className="mini-stat">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}
