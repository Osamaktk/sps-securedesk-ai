export default function StatCard({
  description,
  icon = 'ST',
  title,
  trend,
  trendDirection = 'neutral',
  value,
}) {
  return (
    <article className="stat-card">
      <div className="stat-card__header">
        <span className="stat-card__title">{title}</span>
        <span className="stat-card__icon" aria-hidden="true">
          {icon}
        </span>
      </div>
      <div className="stat-card__value-row">
        <strong>{value}</strong>
        {trend && (
          <span className={`stat-card__trend stat-card__trend--${trendDirection}`}>
            {trend}
          </span>
        )}
      </div>
      {description && <p>{description}</p>}
    </article>
  );
}
