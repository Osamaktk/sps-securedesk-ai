export default function Card({
  actions,
  children,
  className = '',
  subtitle,
  title,
}) {
  return (
    <article className={`card ${className}`.trim()}>
      {(title || subtitle || actions) && (
        <div className="card__header">
          <div>
            {title && <h2 className="card__title">{title}</h2>}
            {subtitle && <p className="card__subtitle">{subtitle}</p>}
          </div>
          {actions && <div className="card__actions">{actions}</div>}
        </div>
      )}
      <div className="card__body">{children}</div>
    </article>
  );
}
