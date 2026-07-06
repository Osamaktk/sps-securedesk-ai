import { useState } from 'react';

export default function CategoryBrowser({
  categories = [],
  expanded,
  onCategoryClick,
  onSubcategoryClick,
  disabled = false,
}) {
  const [filter, setFilter] = useState('');

  const visibleCategories = categories.filter((cat) => {
    if (!filter) return true;
    const q = filter.toLowerCase();
    return (
      cat.label.toLowerCase().includes(q) ||
      cat.subcategories.some((sub) => sub.label.toLowerCase().includes(q))
    );
  });

  return (
    <div className="chat-suggestions" aria-label="Browse helpdesk categories">
      {visibleCategories.length > 1 && (
        <input
          type="search"
          className="category-browser__search"
          placeholder="Search categories..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          disabled={disabled}
        />
      )}

      <div className="category-browser__list">
        {visibleCategories.map((category) => {
          const isExpanded = expanded === category.id;
          const hasChildren = category.subcategories && category.subcategories.length > 0;
          return (
            <div key={category.id} className="category-browser__item">
              <button
                type="button"
                className="category-browser__button"
                disabled={disabled}
                onClick={() => onCategoryClick(category)}
              >
                <span className="category-browser__icon" aria-hidden="true">
                  {category.icon || '?'}
                </span>
                <span>{category.label}</span>
                {hasChildren && (
                  <span className="category-browser__chevron" aria-hidden="true">
                    {isExpanded ? '▲' : '▼'}
                  </span>
                )}
              </button>

              {isExpanded && hasChildren && (
                <div className="category-browser__sub">
                  {category.subcategories.map((sub) => (
                    <button
                      key={sub.id}
                      type="button"
                      className="category-browser__sub-button"
                      disabled={disabled}
                      onClick={() => onSubcategoryClick(sub)}
                    >
                      {sub.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
