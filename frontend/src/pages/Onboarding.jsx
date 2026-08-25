import { useState } from "react";
import { useNavigate } from "react-router-dom";

const SLIDES = [
  {
    title: "Chet tillarni o'zingiz erkin o'rganing",
    text: "Muddat yo'q, bosim yo'q.",
  },
  {
    title: "Xohlagan vaqtda va istalgan joyda o'rganing",
    text: "O'qiymiz, tinglaymiz, takrorlaymiz.",
  },
];

export default function Onboarding() {
  const [slide, setSlide] = useState(0);
  const navigate = useNavigate();
  const current = SLIDES[slide];

  return (
    <div className="onboarding-page">
      <div className="bg-grid" />
      <div className="blobs">
        <span className="blob blob-1" />
        <span className="blob blob-2" />
        <span className="blob blob-3" />
      </div>

      <div key={slide} className="onboard-card glass">
        <span className="logo onboard-logo">LINGUO</span>
        <h1>{current.title}</h1>
        <p>{current.text}</p>

        <button
          className="btn-primary btn-block"
          onClick={() => (slide === 0 ? setSlide(1) : navigate("/login"))}
        >
          {slide === 0 ? "Keyingisi" : "Boshlash"}
        </button>

        <div className="dots">
          {SLIDES.map((_, i) => (
            <span
              key={i}
              className={`dot${i === slide ? " active" : ""}`}
              onClick={() => setSlide(i)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
