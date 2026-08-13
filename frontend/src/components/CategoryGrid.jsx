const categories = [
  ["Age", "Age-targeted abuse"],
  ["Ethnicity", "Ethnicity-targeted abuse"],
  ["Gender", "Gender-targeted abuse"],
  ["Religion", "Religion-targeted abuse"],
  ["Other", "Other cyberbullying"],
  ["Safe", "Not cyberbullying"],
];

export default function CategoryGrid() {
  return (
    <section className="category-section" aria-labelledby="category-title">
      <div className="section-heading">
        <span className="eyebrow">Classification space</span>
        <h2 id="category-title">Six output classes</h2>
      </div>
      <div className="category-grid">
        {categories.map(([title, copy]) => (
          <div className="category-card" key={title}>
            <span className="category-card__marker" />
            <div>
              <strong>{title}</strong>
              <span>{copy}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
