export default function ChatSourceCitation({ citation }) {
  return (
    <span className="chat-citation" title={citation.source || 'Knowledge Base'}>
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M6 4h10a2 2 0 0 1 2 2v14H8a2 2 0 0 1-2-2V4Z" />
        <path d="M9 8h6M9 12h6" />
      </svg>
      Source: {citation.label}
    </span>
  );
}
