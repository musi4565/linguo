export default function Modal({ open, onClose, children }) {
  if (!open) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal glass" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Yopish">
          ✕
        </button>
        {children}
      </div>
    </div>
  );
}
