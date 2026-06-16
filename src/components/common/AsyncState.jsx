import Button from './Button';

export default function AsyncState({
  actionLabel = 'Try again',
  children,
  description,
  onAction,
  title,
  type = 'loading',
}) {
  return (
    <section
      className={`async-state async-state--${type}`}
      role={type === 'error' ? 'alert' : 'status'}
      aria-live="polite"
    >
      <span className="async-state__icon" aria-hidden="true">
        {type === 'loading' ? <i /> : type === 'error' ? '!' : '0'}
      </span>
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      {onAction && (
        <Button variant={type === 'error' ? 'primary' : 'outline'} onClick={onAction}>
          {actionLabel}
        </Button>
      )}
      {children}
    </section>
  );
}
