import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api, apiErrorMessage } from "../api/client";

const SPEEDS = [1, 1.25, 1.5];
const FLAGS = { en: "🇬🇧", ru: "🇷🇺", ar: "🇸🇦", ko: "🇰🇷", tr: "🇹🇷" };

function cleanWord(token) {
  return token.replace(/[^\p{L}\p{N}'’-]/gu, "");
}

export default function Reader() {
  const { bookId } = useParams();
  const [book, setBook] = useState(null);
  const [error, setError] = useState("");
  const [sectionIdx, setSectionIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [rateIdx, setRateIdx] = useState(0);
  const [sentenceIdx, setSentenceIdx] = useState(-1);
  const [savedMsg, setSavedMsg] = useState("");
  const [pop, setPop] = useState(null);
  const [tr, setTr] = useState("");
  const [trState, setTrState] = useState("");
  const [savingWord, setSavingWord] = useState(false);

  const audioRef = useRef(null);
  const sentenceRefs = useRef([]);
  const sessionStartRef = useRef(Date.now());

  useEffect(() => {
    api
      .get(`/books/${bookId}/`)
      .then((res) => {
        setBook(res.data);
        let idx = 0;
        if (res.data.last_section_id) {
          const found = res.data.sections.findIndex(
            (s) => s.id === res.data.last_section_id
          );
          if (found >= 0) idx = found;
        }
        setSectionIdx(idx);
      })
      .catch(() => setError("Kitob yuklanmadi"));
  }, [bookId]);

  const section = book?.sections?.[sectionIdx];
  const timestamps = section?.timestamps || [];

  // Audio manba va tezlikni yangilash
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !section) return;
    setPlaying(false);
    setCurrentTime(0);
    setDuration(0);
    setSentenceIdx(-1);
    audio.pause();
    audio.src = section.audio_url || "";
    audio.load();
    if (audioRef.current) audioRef.current.playbackRate = SPEEDS[rateIdx];
  }, [section?.id]);

  useEffect(() => {
    if (audioRef.current) audioRef.current.playbackRate = SPEEDS[rateIdx];
  }, [rateIdx]);

  // Progressni saqlash
  const saveProgress = useCallback(
    (idx) => {
      if (!book) return;
      const sec = book.sections[idx];
      if (!sec) return;
      const percent = Math.round(((idx + 1) / book.sections.length) * 100);
      api
        .post("/progress/", { book_id: book.id, section_id: sec.id, percent })
        .catch(() => {});
    },
    [book]
  );

  function goToSection(idx) {
    if (!book || idx < 0 || idx >= book.sections.length) return;
    saveProgress(sectionIdx); // ketayotgan joydan oldingisini saqla
    setSectionIdx(idx);
    sessionStartRef.current = Date.now();
  }

  // Har 60 sekundda sessiyani yozib borish (o'ynayotganda)
  useEffect(() => {
    if (!playing || !book) return;
    const timer = setInterval(() => {
      api
        .post("/stats/log-session/", {
          minutes: 1,
          language_id: book.language.id,
        })
        .catch(() => {});
    }, 60000);
    return () => clearInterval(timer);
  }, [playing, book]);

  function renderTokens(sentence, sentIdx) {
    return String(sentence)
      .split(/(\s+)/)
      .map((part, k) => {
        if (!part || /^\s+$/.test(part)) return part;
        const clean = cleanWord(part);
        if (!clean) return <span key={k}>{part}</span>;
        return (
          <span key={k} className="tap-word" onClick={() => openWord(clean, sentIdx)}>
            {part}
          </span>
        );
      });
  }

  function handleTimeUpdate() {
    const audio = audioRef.current;
    if (!audio) return;
    setCurrentTime(audio.currentTime);

    for (let i = 0; i < timestamps.length; i++) {
      const t = timestamps[i];
      if (audio.currentTime >= t.start && audio.currentTime < t.end) {
        if (i !== sentenceIdx) {
          setSentenceIdx(i);
          sentenceRefs.current[i]?.scrollIntoView({
            behavior: "smooth",
            block: "center",
          });
        }
        break;
      }
    }
  }

  function togglePlay() {
    const audio = audioRef.current;
    if (!audio || !section?.audio_url) return;
    if (playing) {
      audio.pause();
    } else {
      audio.play().then(() => setPlaying(true)).catch(() => {});
    }
  }

  async function addToBookmarks() {
    try {
      await api.post("/bookmarks/", { book_id: Number(bookId) });
      setSavedMsg("Xatcho'pka qo'shildi ✓");
      setTimeout(() => setSavedMsg(""), 2000);
    } catch (err) {
      setSavedMsg(apiErrorMessage(err));
      setTimeout(() => setSavedMsg(""), 2500);
    }
  }

  function openWord(clean, sentIdx) {
    setPop({ word: clean, sentIdx });
    setTr("");
    setTrState("loading");
  }

  useEffect(() => {
    if (!pop) return undefined;
    let alive = true;
    api
      .get("/translate-word/", { params: { word: pop.word, lang: book?.language?.code } })
      .then((r) => {
        if (!alive) return;
        if (r.data?.translation) {
          setTr(r.data.translation);
          setTrState("ok");
        } else {
          setTr("");
          setTrState("fail");
        }
      })
      .catch(() => {
        if (alive) {
          setTr("");
          setTrState("fail");
        }
      });
    return () => {
      alive = false;
    };
  }, [pop, book]);

  useEffect(() => {
    function onKey(e) {
      if (e.key === "Escape") setPop(null);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  async function saveWord() {
    if (!pop || !tr.trim()) return;
    setSavingWord(true);
    try {
      await api.post("/saved-words/", {
        language_id: book.language.id,
        word: pop.word,
        translation: tr.trim(),
        source_book_id: book.id,
      });
      setPop(null);
      setSavedMsg(`"${pop.word}" so'zlarga saqlandi ✓`);
      setTimeout(() => setSavedMsg(""), 2200);
    } catch (err) {
      setSavedMsg(apiErrorMessage(err));
      setTimeout(() => setSavedMsg(""), 2500);
    } finally {
      setSavingWord(false);
    }
  }

  if (error) return <div className="empty-state glass">{error}</div>;
  if (!book) return <div className="loading">Yuklanmoqda...</div>;

  return (
    <div className="reader-page">
      <div className="reader-topbar">
        <Link to={`/courses/${book.language.id}`} className="back-link">
          ← Orqaga
        </Link>
        <div className="reader-meta">
          <strong>{book.topic}</strong>
          <span>
            Bo'lim {sectionIdx + 1} / {book.sections.length}
          </span>
        </div>
        <button className="btn-ghost" onClick={addToBookmarks}>
          ☆ Xatcho'pka
        </button>
      </div>
      {savedMsg && <div className="save-toast glass">{savedMsg}</div>}

      {/* MUHIM: divider alohida grid ustuni — grid-template-columns: 1fr 1px 1fr */}
      <div className="reader-grid glass">
        <div className="reader-col original" lang={book.language.code}>
          {(section.sentences || []).map((sentence, i) => (
            <span
              key={i}
              ref={(el) => (sentenceRefs.current[i] = el)}
              className={`sentence${i === sentenceIdx ? " current" : ""}`}
            >
              {renderTokens(sentence, i)}{" "}
            </span>
          ))}
        </div>

        <div className="reader-divider" />

        <div className="reader-col translation">
          {(section.translated_sentences ||
            (section.translated_text ? [section.translated_text] : [])).map((s, i) => (
            <span key={i} className={`sentence${i === sentenceIdx ? " current-tr" : ""}`}>
              {s}{" "}
            </span>
          ))}
        </div>
      </div>

      <div className="player glass">
        <button
          className={`play-btn${playing ? " playing" : ""}`}
          onClick={togglePlay}
          disabled={!section?.audio_url}
          title={playing ? "Pauza" : "Ijro"}
        >
          {playing ? "❚❚" : "▶"}
        </button>

        <div className="player-track">
          <input
            type="range"
            min={0}
            max={duration || 0}
            step={0.05}
            value={currentTime}
            onChange={(e) => {
              const t = parseFloat(e.target.value);
              if (audioRef.current) audioRef.current.currentTime = t;
              setCurrentTime(t);
            }}
            style={{ "--fill": duration ? `${(currentTime / duration) * 100}%` : "0%" }}
          />
          <div className="player-times">
            <span>{fmt(currentTime)}</span>
            <span>{fmt(duration)}</span>
          </div>
        </div>

        <button className="speed-btn" onClick={() => setRateIdx((rateIdx + 1) % SPEEDS.length)}>
          {SPEEDS[rateIdx].toFixed(2).replace(/\.?0+$/, "")}x
        </button>
      </div>
      {!section?.audio_url && (
        <p className="no-audio-note">Bu bo'lim uchun audio hali tayyorlanmagan.</p>
      )}

      {pop && (
        <div className="word-pop glass">
          <div className="word-pop-head">
            <span className="word-flag">{FLAGS[book.language.code] || "🌐"}</span>
            <strong className="word-pop-word">{pop.word}</strong>
            <button className="icon-btn danger" title="Yopish" onClick={() => setPop(null)}>
              ✕
            </button>
          </div>
          <label className="field word-pop-field">
            Tarjimasi (o'zbekcha)
            {trState === "loading" ? (
              <input value="" placeholder="Tarjima olinmoqda..." readOnly />
            ) : (
              <input
                value={tr}
                onChange={(e) => setTr(e.target.value)}
                placeholder={
                  trState === "fail" ? "Avto-tarjima topilmadi — qo'lda yozing" : "Tarjimani tahrirlash mumkin"
                }
                autoFocus
              />
            )}
          </label>
          {section?.translated_sentences?.[pop.sentIdx] && (
            <p className="word-pop-context">
              Kontekst: {section.translated_sentences[pop.sentIdx]}
            </p>
          )}
          <button
            className="btn-primary btn-block"
            disabled={!tr.trim() || savingWord}
            onClick={saveWord}
          >
            ☆ So'zlarga saqlash
          </button>
        </div>
      )}

      <div className="section-nav">
        <button
          className="btn-ghost"
          disabled={sectionIdx === 0}
          onClick={() => goToSection(sectionIdx - 1)}
        >
          ← Oldingi bo'lim
        </button>
        <div className="progress-bar thin wide">
          <span
            className="progress-fill"
            style={{
              width: `${Math.round(((sectionIdx + 1) / book.sections.length) * 100)}%`,
            }}
          />
        </div>
        <button
          className="btn-primary"
          disabled={sectionIdx === book.sections.length - 1}
          onClick={() => goToSection(sectionIdx + 1)}
        >
          Keyingi bo'lim →
        </button>
      </div>

      <audio
        ref={audioRef}
        preload="auto"
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={(e) => setDuration(e.target.duration || 0)}
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        onEnded={() => {
          setPlaying(false);
          setSentenceIdx(-1);
          saveProgress(sectionIdx);
        }}
      />
    </div>
  );
}

function fmt(seconds) {
  if (!seconds && seconds !== 0) return "0:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${String(s).padStart(2, "0")}`;
}
