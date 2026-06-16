export default function ChatHeader({ onClose }) {
  return (
    <header className="chat-header">
      <div className="chat-header__identity">
        <span className="chat-header__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <path d="M12 3 5 6v5c0 4.8 2.8 8.4 7 10 4.2-1.6 7-5.2 7-10V6l-7-3Z" />
            <path d="M9 11h6M9 14h4" />
          </svg>
        </span>
        <div>
          <strong>SPS SecureDesk AI</strong>
          <span>
            <i aria-hidden="true" />
            Knowledge-base assistant
          </span>
        </div>
      </div>
      <button
        className="chat-header__close"
        type="button"
        aria-label="Minimize SecureDesk AI"
        onClick={onClose}
      >
        <span aria-hidden="true">-</span>
      </button>
    </header>
  );
}
