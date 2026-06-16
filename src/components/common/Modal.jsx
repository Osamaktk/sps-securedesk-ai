import { useEffect, useId } from 'react';
import Button from './Button';

export default function Modal({
  children,
  confirmLabel = 'Confirm',
  isOpen,
  onClose,
  onConfirm,
  subtitle,
  title,
}) {
  const titleId = useId();

  useEffect(() => {
    if (!isOpen) return undefined;

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') onClose?.();
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose?.();
      }}
    >
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
      >
        <div className="modal__header">
          <div>
            <h2 id={titleId}>{title}</h2>
            {subtitle && <p>{subtitle}</p>}
          </div>
          <button
            className="icon-button"
            type="button"
            aria-label="Close modal"
            onClick={onClose}
          >
            X
          </button>
        </div>
        <div className="modal__body">{children}</div>
        <div className="modal__footer">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          {onConfirm && <Button onClick={onConfirm}>{confirmLabel}</Button>}
        </div>
      </section>
    </div>
  );
}
