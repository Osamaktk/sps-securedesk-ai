export default function EmptyState({
  action,
  description,
  icon = 'SPS',
  title,
}) {
  return (
    <div className="empty-state">
      <div className="empty-state__mark" aria-hidden="true">
        {icon}
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action && <div className="empty-state__action">{action}</div>}
    </div>
  );
}
