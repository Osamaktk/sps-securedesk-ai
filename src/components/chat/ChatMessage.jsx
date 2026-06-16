import ChatSourceCitation from './ChatSourceCitation';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`chat-message chat-message--${isUser ? 'user' : 'assistant'}`}>
      {!isUser && (
        <span className="chat-message__avatar" aria-hidden="true">
          AI
        </span>
      )}
      <div className="chat-message__content">
        <div className="chat-message__bubble">{message.content}</div>
        {message.citations?.length > 0 && (
          <div className="chat-message__citations">
            {message.citations.map((citation) => (
              <ChatSourceCitation citation={citation} key={citation.id} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
