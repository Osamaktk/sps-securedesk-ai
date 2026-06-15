export const requestCategories = [
  'Cloud',
  'Cybersecurity',
  'Identity and Access',
  'DevOps',
  'Internship/HR',
  'General IT',
];

export default function CategorySelect({ id = 'request-category', onChange, value }) {
  return (
    <label className="request-field" htmlFor={id}>
      <span>Category</span>
      <select id={id} name="category" required value={value} onChange={onChange}>
        <option value="">Select the best category</option>
        {requestCategories.map((category) => (
          <option key={category} value={category}>
            {category}
          </option>
        ))}
      </select>
      <small>Used to route the request to the right support team.</small>
    </label>
  );
}
