import { ArrowIcon, SparkIcon } from "./Icons";

export default function ReviewComposer({
  value,
  onChange,
  onSubmit,
  loading,
  disabled,
}) {
  const maxLength = 2000;

  function handleKeyDown(event) {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      if (!disabled && !loading) onSubmit();
    }
  }

  return (
    <div className="composer-shell">
      <div className="composer-topline">
        <span className="composer-label"><SparkIcon size={16} /> Review analyzer</span>
        <span className="composer-counter">{value.length}/{maxLength}</span>
      </div>

      <textarea
        className="review-input"
        value={value}
        onChange={(event) => onChange(event.target.value.slice(0, maxLength))}
        onKeyDown={handleKeyDown}
        placeholder="Write or paste a review, tweet or message to classify..."
        aria-label="Review text"
        rows={6}
      />

      <div className="composer-footer">
        <span className="shortcut-hint">Ctrl/⌘ + Enter to analyze</span>
        <button
          className="analyze-button"
          type="button"
          onClick={onSubmit}
          disabled={disabled || loading}
        >
          {loading ? (
            <>
              <span className="spinner" />
              Analyzing with BERT
            </>
          ) : (
            <>
              Analyze review
              <ArrowIcon size={18} />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
