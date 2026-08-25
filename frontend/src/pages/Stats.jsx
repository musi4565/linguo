import { useEffect, useState } from "react";

import { api } from "../api/client";

const DAY_LABELS = ["Ya", "Du", "Se", "Ch", "Pa", "Ju", "Sh"];

export default function Stats() {
  const [daily, setDaily] = useState(null);
  const [weekly, setWeekly] = useState(null);
  const [byLang, setByLang] = useState(null);

  useEffect(() => {
    Promise.all([
      api.get("/stats/daily/"),
      api.get("/stats/weekly/"),
      api.get("/stats/by-language/"),
    ])
      .then(([d, w, l]) => {
        setDaily(d.data);
        setWeekly(w.data);
        setByLang(l.data);
      })
      .catch(() => {
        setDaily({});
        setWeekly({ week: [] });
        setByLang({ languages: [] });
      });
  }, []);

  if (!daily || !weekly || !byLang) return <div className="loading">Yuklanmoqda...</div>;

  const maxMinutes = Math.max(...weekly.week.map((d) => d.minutes), 1);
  const goalPercent = Math.min(
    Math.round((weekly.today_minutes / (weekly.daily_goal_minutes || 30)) * 100),
    100
  );

  return (
    <div className="stats-page">
      <div className="metric-grid">
        <MetricCard icon="🔥" value={daily.streak} label="ketma-ket kunlar" />
        <MetricCard icon="📚" value={daily.words_learned} label="o'rganilgan so'zlar" />
        <MetricCard icon="✅" value={daily.lessons_completed} label="tugallangan darslar" />
        <MetricCard icon="⏱️" value={`${daily.total_minutes}`} label="jami daqiqa" />
      </div>

      <div className="stats-row">
        <section className="panel glass weekly-panel">
          <h3>Haftalik faollik</h3>
          <div className="bar-chart">
            {weekly.week.map((d, i) => {
              const date = new Date(d.date + "T00:00:00");
              const isToday = i === weekly.week.length - 1;
              return (
                <div key={d.date} className="bar-col">
                  <span className="bar-value">{d.minutes > 0 ? d.minutes : ""}</span>
                  <div
                    className={`bar${isToday ? " today" : ""}`}
                    style={{ height: `${Math.max((d.minutes / maxMinutes) * 100, 4)}%` }}
                    title={`${d.minutes} daqiqa`}
                  />
                  <span className="bar-label">
                    {DAY_LABELS[date.getDay()]}
                  </span>
                </div>
              );
            })}
          </div>
        </section>

        <section className="panel glass goal-panel">
          <h3>Bugungi maqsad</h3>
          <div
            className="goal-ring"
            style={{ "--p": goalPercent }}
          >
            <div className="goal-center">
              <strong>{weekly.today_minutes}</strong>
              <span>/ {weekly.daily_goal_minutes} daq</span>
            </div>
          </div>
          <p className="goal-note">
            {goalPercent >= 100
              ? "Bugungi maqsad bajarildi! 🎉"
              : `Yana ${Math.max(weekly.daily_goal_minutes - weekly.today_minutes, 0)} daqiqa qoldi`}
          </p>
        </section>
      </div>

      <section className="panel glass lang-dist">
        <h3>Tillar bo'yicha vaqt taqsimoti</h3>
        {byLang.languages.every((l) => l.minutes === 0) && (
          <p className="muted">Hozircha faollik yozilmagan — o'qishni boshlang!</p>
        )}
        <ul className="dist-list">
          {byLang.languages.map((l) => (
            <li key={l.language_id}>
              <span className="dist-name">{l.name}</span>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${l.percent}%` }} />
              </div>
              <span className="dist-num">{l.percent}%</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function MetricCard({ icon, value, label }) {
  return (
    <div className="metric-card glass">
      <span className="metric-icon">{icon}</span>
      <strong>{value}</strong>
      <span className="metric-label">{label}</span>
    </div>
  );
}
