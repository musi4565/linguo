import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../api/client";

const FLAGS = { en: "🇬🇧", ru: "🇷🇺", ar: "🇸🇦", ko: "🇰🇷", tr: "🇹🇷" };

export default function Bookmarks() {
  const [tab, setTab] = useState("lessons");
  const [bookmarks, setBookmarks] = useState(null);
  const [words, setWords] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/bookmarks/").then((r) => setBookmarks(r.data)).catch(() => setBookmarks([]));
    api.get("/saved-words/").then((r) => setWords(r.data)).catch(() => setWords([]));
  }, []);

  async function removeBookmark(id) {
    await api.delete(`/bookmarks/${id}/`);
    setBookmarks(bookmarks.filter((b) => b.id !== id));
  }

  async function removeWord(id) {
    await api.delete(`/saved-words/${id}/`);
    setWords(words.filter((w) => w.id !== id));
  }

  return (
    <div className="bookmarks-page">
      <div className="tabs">
        <button
          className={`tab${tab === "lessons" ? " active" : ""}`}
          onClick={() => setTab("lessons")}
        >
          Darslar
        </button>
        <button
          className={`tab${tab === "words" ? " active" : ""}`}
          onClick={() => setTab("words")}
        >
          So'zlar
        </button>
      </div>

      {tab === "lessons" && (
        <>
          {bookmarks === null ? (
            <div className="loading">Yuklanmoqda...</div>
          ) : bookmarks.length === 0 ? (
            <div className="empty-state glass">
              Hozircha saqlangan dars yo'q. O'qish rejimida ☆ tugmasi bilan qo'shing.
            </div>
          ) : (
            <ul className="lesson-list">
              {bookmarks.map((b) => (
                <li key={b.id} className="lesson-row glass">
                  <img src={b.book.cover_image_url} alt="" className="lesson-thumb" />
                  <div className="lesson-info">
                    <strong>{b.book.topic}</strong>
                    <span>
                      {FLAGS[b.book.language.code]} {b.book.language.name}
                    </span>
                  </div>
                  <button className="btn-ghost" onClick={() => navigate(`/read/${b.book.id}`)}>
                    Ochish
                  </button>
                  <button
                    className="icon-btn danger"
                    title="O'chirish"
                    onClick={() => removeBookmark(b.id)}
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          )}
        </>
      )}

      {tab === "words" && (
        <>
          {words === null ? (
            <div className="loading">Yuklanmoqda...</div>
          ) : words.length === 0 ? (
            <div className="empty-state glass">Hozircha so'z saqlanmagan.</div>
          ) : (
            <div className="words-grid">
              {words.map((w) => (
                <div key={w.id} className="word-card glass">
                  <div className="word-card-head">
                    <span className="word-flag">{FLAGS[w.language.code] || "🌐"}</span>
                    <button
                      className="icon-btn danger"
                      title="O'chirish"
                      onClick={() => removeWord(w.id)}
                    >
                      ✕
                    </button>
                  </div>
                  <strong>{w.word}</strong>
                  <span className="word-tr">{w.translation}</span>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
