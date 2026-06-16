export default function Brand({ compact = false }) {
  return (
    <div className="brand" aria-label="SPS SecureDesk AI">
      <img className="brand__logo" src="/logo.png" alt="" />
      {!compact && (
        <div>
          <span className="brand__name">SecureDesk AI</span>
          <span className="brand__tagline">Enterprise Helpdesk</span>
        </div>
      )}
    </div>
  );
}
