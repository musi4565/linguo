import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../api/client";

export default function CourseBooks() {
  const { langId } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    setData(null);
    api
      .get(`/languages/${langId}/books/`)
      .then((r) => setData(r.data))
      .catch(() => setError("Kitoblar yuklanmadi"));
  }, [langId]);

  if (error) return <div className="empty-state glass">{error}</div>;
  if (!data) return <div className="loading">Yuklanmoqda...</div>;

  return (
    <div className="course-books-page">
      <Link to="/courses" className="back-link">
        ← Tillar ro'yxati
      </Link>
      <h2 className="section-title">{data.name} — kitoblar</h2>

      <div className="books-grid">
        {data.books.map((book) => (
          <button
            key={book.id}
            className="book-card"
            onClick={() => navigate(`/read/${book.id}`)}
          >
            {book.is_featured && <span className="badge-top">Top tanlov</span>}
            <span
              className="book-cover"
              style={{ backgroundImage: `url(${book.cover_image_url})` }}
            />
            <span className="book-body">
              <strong>
                {book.emoji} {book.topic}
              </strong>
              {book.percent_complete > 0 ? (
                <>
                  <span className="progress-bar thin">
                    <span className="progress-fill" style={{ width: `${book.percent_complete}%` }} />
                  </span>
                  <em>{book.percent_complete}% tugallangan</em>
                </>
              ) : (
                <em>Boshlash →</em>
              )}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
