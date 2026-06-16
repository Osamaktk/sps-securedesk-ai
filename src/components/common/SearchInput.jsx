export default function SearchInput({
  className = '',
  onChange,
  placeholder = 'Search',
  value,
  ...props
}) {
  return (
    <label className={`search-input ${className}`.trim()}>
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-4-4" />
      </svg>
      <input
        type="search"
        aria-label={props['aria-label'] || placeholder}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        {...props}
      />
    </label>
  );
}
