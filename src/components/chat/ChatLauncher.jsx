import { useState } from 'react';
import ChatWindow from './ChatWindow';

export default function ChatLauncher() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="chat-widget">
      {isOpen && <ChatWindow onClose={() => setIsOpen(false)} />}
      <button
        className={`chat-launcher ${isOpen ? 'chat-launcher--open' : ''}`}
        type="button"
        aria-expanded={isOpen}
        aria-label={isOpen ? 'Close SecureDesk AI' : 'Open SecureDesk AI'}
        onClick={() => setIsOpen((value) => !value)}
      >
        <span className="chat-launcher__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <path d="M12 3 5 6v5c0 4.8 2.8 8.4 7 10 4.2-1.6 7-5.2 7-10V6l-7-3Z" />
            <path d="M8.5 10.2h7M8.5 13.5h4.5" />
          </svg>
        </span>
        <span>{isOpen ? 'Close Assistant' : 'SecureDesk AI'}</span>
      </button>
    </div>
  );
}
