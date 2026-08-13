import { useState } from "react";
import CategoryGrid from "./components/CategoryGrid";
import ModelBadge from "./components/ModelBadge";
import PredictionPanel from "./components/PredictionPanel";
import ReviewComposer from "./components/ReviewComposer";
import { ShieldIcon } from "./components/Icons";

const examples = [
  "You are too old to understand anything about social media.",
  "People of your religion should not be allowed here.",
  "Thanks for sharing this — I completely agree with your point.",
];

export default function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function analyze() {
    const cleaned = text.trim();

    if (cleaned.length < 3) {
      setError("Please enter at least 3 characters before analyzing.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: cleaned }),
      });

      const payload = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(payload.detail || payload.error || "Prediction service is unavailable.");
      }

      setResult(payload);
    } catch (requestError) {
      setError(
        requestError?.message ||
          "Could not connect to the prediction API. Check the deployment configuration."
      );
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setText("");
    setResult(null);
    setError("");
  }

  return (
    <main className="app-shell">
      <div className="ambient ambient--one" />
      <div className="ambient ambient--two" />

      <nav className="topbar">
        <a className="brand" href="/" aria-label="CyberShield AI home">
          <span className="brand-mark"><ShieldIcon size={22} /></span>
          <span>
            <strong>CyberShield</strong>
            <em>AI</em>
          </span>
        </a>

        <div className="topbar-right">
          <span className="research-pill">CSE440 Project</span>
          <ModelBadge />
        </div>
      </nav>

      <section className="hero">
        <div className="hero-copy">
          <span className="hero-kicker">
            <span className="live-dot" />
            Intelligent text safety classification
          </span>
          <h1>
            Understand the <span>intent</span> behind the message.
          </h1>
          <p>
            Paste a review, tweet or message. Our best-performing fine-tuned
            BERT model predicts one of six cyberbullying classes and returns
            an interpretable confidence score.
          </p>
        </div>

        <div className="workspace">
          <div className="workspace-header">
            <div>
              <span className="eyebrow">Live classifier</span>
              <h2>Analyze a message</h2>
            </div>
            <div className="metric-pair">
              <span><strong>0.897</strong> Macro-F1</span>
              <span><strong>6</strong> classes</span>
            </div>
          </div>

          <ReviewComposer
            value={text}
            onChange={setText}
            onSubmit={analyze}
            loading={loading}
            disabled={text.trim().length < 3}
          />

          <div className="examples">
            <span>Try an example</span>
            <div className="example-list">
              {examples.map((example, index) => (
                <button
                  key={example}
                  type="button"
                  onClick={() => {
                    setText(example);
                    setResult(null);
                    setError("");
                  }}
                >
                  {index === 2 ? "Neutral" : index === 0 ? "Age-based" : "Religion-based"}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="error-card" role="alert">
              <strong>Unable to analyze</strong>
              <span>{error}</span>
            </div>
          )}

          <PredictionPanel result={result} onReset={reset} />
        </div>
      </section>

      <CategoryGrid />

      <section className="model-story">
        <div>
          <span className="eyebrow">Why this model</span>
          <h2>Selected from the full benchmark, not chosen by assumption.</h2>
        </div>
        <div className="model-story__stats">
          <article>
            <strong>90.64%</strong>
            <span>Test accuracy</span>
          </article>
          <article>
            <strong>0.897</strong>
            <span>Macro-F1</span>
          </article>
          <article>
            <strong>BERT</strong>
            <span>Best model</span>
          </article>
        </div>
      </section>

      <footer>
        <div>
          <strong>CyberShield AI</strong>
          <span>Research demonstration for CSE440.</span>
        </div>
        <p>
          Predictions are model outputs for academic demonstration and should
          not be treated as a final moderation or disciplinary decision.
        </p>
      </footer>
    </main>
  );
}
