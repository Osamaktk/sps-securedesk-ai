const valueTones = {
  email: 'blue',
  portal_form: 'navy',
  chat: 'purple',
  open: 'blue',
  pending: 'amber',
  resolved: 'green',
  closed: 'gray',
  low: 'gray',
  medium: 'blue',
  high: 'amber',
  critical: 'red',
  safe: 'green',
  guarded: 'amber',
  elevated: 'red',
};

export default function Badge({ children, className = '', tone, value }) {
  const content = children ?? String(value || '').replaceAll('_', ' ');
  const resolvedTone = tone || valueTones[value] || 'gray';

  return (
    <span className={`badge badge--${resolvedTone} ${className}`.trim()}>
      {content}
    </span>
  );
}
