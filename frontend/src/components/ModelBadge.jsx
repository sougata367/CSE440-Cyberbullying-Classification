import { SparkIcon } from "./Icons";

export default function ModelBadge() {
  return (
    <div className="model-badge" aria-label="Best model performance">
      <span className="model-badge__icon"><SparkIcon size={16} /></span>
      <span>BERT Base</span>
      <span className="model-badge__dot" />
      <strong>90.64%</strong>
      <span className="model-badge__muted">test accuracy</span>
    </div>
  );
}
