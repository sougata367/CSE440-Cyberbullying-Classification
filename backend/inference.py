from functools import lru_cache
from huggingface_hub import InferenceClient

from backend.config import HF_PROVIDER, HF_TOKEN, MODEL_ID, MODEL_NAME
from backend.labels import canonicalize_label, display_label


class ModelConfigurationError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_client():
    if not HF_TOKEN:
        raise ModelConfigurationError(
            "HF_TOKEN is not configured on the server."
        )

    if not MODEL_ID:
        raise ModelConfigurationError(
            "HF_MODEL_ID is not configured on the server."
        )

    return InferenceClient(
        provider=HF_PROVIDER,
        api_key=HF_TOKEN,
    )


def _extract_item(item):
    if isinstance(item, dict):
        label = item.get("label")
        score = item.get("score", 0.0)
    else:
        label = getattr(item, "label", None)
        score = getattr(item, "score", 0.0)

    canonical = canonicalize_label(label)

    return {
        "label": canonical,
        "display_label": display_label(canonical),
        "score": float(score or 0.0),
    }


def classify_text(text: str):
    client = get_client()

    raw_output = client.text_classification(
        text,
        model=MODEL_ID,
        top_k=6,
    )

    # Some client/provider versions can wrap a single input in one extra list.
    if (
        isinstance(raw_output, list)
        and raw_output
        and isinstance(raw_output[0], list)
    ):
        raw_output = raw_output[0]

    probabilities = [_extract_item(item) for item in (raw_output or [])]
    probabilities.sort(key=lambda item: item["score"], reverse=True)

    if not probabilities:
        raise RuntimeError("The model returned no classification scores.")

    best = probabilities[0]

    return {
        "prediction": best["label"],
        "display_label": best["display_label"],
        "confidence": best["score"],
        "confidence_percent": round(best["score"] * 100, 2),
        "model": MODEL_NAME,
        "model_id": MODEL_ID,
        "probabilities": probabilities,
    }
