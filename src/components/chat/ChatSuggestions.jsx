const suggestions = [
  'VPN help',
  'Report phishing',
  'Cloud VM issue',
  'Request access',
  'Create ticket',
];

export default function ChatSuggestions({ disabled = false, onSelect }) {
  return (
    <div className="chat-suggestions" aria-label="Suggested helpdesk questions">
      {suggestions.map((suggestion) => (
        <button
          type="button"
          disabled={disabled}
          key={suggestion}
          onClick={() => onSelect(suggestion)}
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
}
