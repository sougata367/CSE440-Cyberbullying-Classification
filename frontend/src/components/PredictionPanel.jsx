import { RefreshIcon, ShieldIcon } from "./Icons";

const safeLabels = new Set(["not_cyberbullying", "not cyberbullying"]);

function normalizeLabel(label = "") {
  return label.toLowerCase().replaceAll("-", "_").replaceAll(" ", "_");
}

export default function PredictionPanel({ result, onReset }) {
  if (!result) return null;

  const isSafe = safeLabels.has(normalizeLabel(result.prediction));
  const probabilities = Array.isArray(result.probabilities)
    ? result.probabilities.slice(0, 6)
    : [];

  return (
    <section className={`prediction-panel ${isSafe ? "prediction-panel--safe" : ""}`}>
      <div className="prediction-panel__glow" />

      <div className="prediction-header">
        <div className="prediction-icon">
          <ShieldIcon size={24} />
        </div>
        <div>
          <span className="eyebrow">Prediction</span>
          <h2>{result.display_label}</h2>
        </div>
        <span className={`status-chip ${isSafe ? "status-chip--safe" : ""}`}>
          {isSafe ? "No cyberbullying detected" : "Cyberbullying detected"}
        </span>
      </div>

      <div className="confidence-card">
        <div className="confidence-row">
          <span>Model confidence</span>
          <strong>{Number(result.confidence_percent ?? result.confidence * 100).toFixed(2)}%</strong>
        </div>
        <div className="confidence-track">
          <div
            className="confidence-fill"
            style={{ width: `${Math.min(100, Math.max(0, Number(result.confidence_percent ?? result.confidence * 100)))}%` }}
          />
        </div>
        <div className="confidence-meta">
          <span>Model: <strong>{result.model || "BERT Base"}</strong></span>
          <span>6-class classifier</span>
        </div>
      </div>

      {probabilities.length > 0 && (
        <div className="probability-list">
          <div className="probability-list__title">Class probabilities</div>
          {probabilities.map((item) => (
            <div className="probability-row" key={item.label}>
              <span>{item.display_label || item.label}</span>
              <div className="probability-track">
                <div
                  className="probability-fill"
                  style={{ width: `${Math.max(1.5, item.score * 100)}%` }}
                />
              </div>
              <strong>{(item.score * 100).toFixed(1)}%</strong>
            </div>
          ))}
        </div>
      )}

      <button className="secondary-button" type="button" onClick={onReset}>
        <RefreshIcon />
        Analyze another review
      </button>
    </section>
  );
}
