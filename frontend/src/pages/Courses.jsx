import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../api/client";

export default function Courses() {
  const [languages, setLanguages] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    api
      .get("/languages/")
      .then((r) => setLanguages(r.data))
      .catch(() => setLanguages([]));
  }, []);

  return (
    <div className="courses-page">
      <h2 className="section-title">Tillar bo'yicha kurslaringiz</h2>
      {languages === null ? (
        <div className="loading">Yuklanmoqda...</div>
      ) : (
        <ul className="course-list">
          {languages.map((lang) => (
            <li key={lang.id}>
              <button className="course-row glass" onClick={() => navigate(`/courses/${lang.id}`)}>
                <img src={lang.cover_image_url} alt="" className="course-cover" />
                <div className="course-info">
                  <strong>{lang.name}</strong>
                  <span>{lang.description}</span>
                </div>
                <div className="course-progress">
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${lang.percent_complete}%` }}
                    />
                  </div>
                  <span className="progress-num">{lang.percent_complete}%</span>
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
