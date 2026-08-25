import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../api/client";

export default function Home() {
  const [languages, setLanguages] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .get("/languages/")
      .then((res) => setLanguages(res.data))
      .catch(() => setLanguages([]));
  }, []);

  return (
    <div className="home-page">
      <section className="banner">
        <div className="banner-inner">
          <h1>
            Xohlagan tilni,
            <br />
            xohlagan vaqtda o'rganing
          </h1>
          <p>
            Kitob o'qing, tinglang va takrorlang — muddat yo'q, bosim yo'q.
          </p>
        </div>
        <span className="banner-orb orb-a" />
        <span className="banner-orb orb-b" />
      </section>

      <h2 className="section-title">Tillar</h2>

      {languages === null ? (
        <div className="loading">Yuklanmoqda...</div>
      ) : (
        <div className="lang-grid">
          {languages.map((lang) => (
            <button
              key={lang.id}
              className="lang-card"
              onClick={() => navigate(`/courses/${lang.id}`)}
              style={{ backgroundImage: `url(${lang.cover_image_url})` }}
            >
              {lang.is_featured && <span className="badge-top">Top tanlov</span>}
              <span className="lang-card-overlay" />
              <span className="lang-card-body">
                <strong>{lang.name}</strong>
                <em>Erkin o'rganish</em>
                {lang.percent_complete > 0 && (
                  <span className="mini-percent">{lang.percent_complete}% tugallangan</span>
                )}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
