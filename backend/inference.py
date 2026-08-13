import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import onnxruntime as ort
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer

from backend.config import HF_TOKEN, MODEL_ID, MODEL_NAME
from backend.labels import ID_TO_LABEL, display_label


# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------

MAX_LENGTH = 64

MODEL_SUBFOLDER = "onnx-int8"
ONNX_FILENAME = "model_quantized.onnx"

MODEL_ROOT = Path("/tmp/cse440_model")
MODEL_DIR = MODEL_ROOT / MODEL_SUBFOLDER
MODEL_PATH = MODEL_DIR / ONNX_FILENAME


class ModelConfigurationError(RuntimeError):
    pass


# ---------------------------------------------------------
# DOWNLOAD MODEL FROM HUGGING FACE
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def prepare_model_files():
    if not MODEL_ID:
        raise ModelConfigurationError(
            "HF_MODEL_ID is not configured on the server."
        )

    MODEL_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Download only the ONNX INT8 deployment folder.
    snapshot_download(
        repo_id=MODEL_ID,
        repo_type="model",
        token=HF_TOKEN or None,
        allow_patterns=[
            f"{MODEL_SUBFOLDER}/*"
        ],
        local_dir=str(MODEL_ROOT),
    )

    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"ONNX model was not found at {MODEL_PATH}"
        )

    return MODEL_DIR


# ---------------------------------------------------------
# LOAD TOKENIZER
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_tokenizer():
    model_dir = prepare_model_files()

    tokenizer = AutoTokenizer.from_pretrained(
        str(model_dir),
        local_files_only=True,
    )

    return tokenizer


# ---------------------------------------------------------
# LOAD ONNX MODEL
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_session():
    prepare_model_files()

    session_options = ort.SessionOptions()

    # Keep CPU usage predictable on serverless runtime.
    session_options.intra_op_num_threads = 1
    session_options.inter_op_num_threads = 1

    session_options.graph_optimization_level = (
        ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    )

    session = ort.InferenceSession(
        str(MODEL_PATH),
        sess_options=session_options,
        providers=[
            "CPUExecutionProvider"
        ],
    )

    return session


# ---------------------------------------------------------
# SOFTMAX
# ---------------------------------------------------------

def softmax(logits):
    logits = np.asarray(
        logits,
        dtype=np.float64,
    )

    shifted = logits - np.max(logits)

    exp_values = np.exp(shifted)

    return exp_values / np.sum(exp_values)


# ---------------------------------------------------------
# CLASSIFICATION
# ---------------------------------------------------------

def classify_text(text: str):
    tokenizer = get_tokenizer()
    session = get_session()

    # Same maximum token length used during BERT training.
    encoded = tokenizer(
        text,
        return_tensors="np",
        truncation=True,
        max_length=MAX_LENGTH,
        padding=False,
    )

    # Only send inputs that actually exist in the ONNX graph.
    required_inputs = {
        item.name
        for item in session.get_inputs()
    }

    ort_inputs = {}

    for name, value in encoded.items():
        if name in required_inputs:
            ort_inputs[name] = np.asarray(
                value,
                dtype=np.int64,
            )

    missing_inputs = (
        required_inputs
        - set(ort_inputs.keys())
    )

    if missing_inputs:
        raise RuntimeError(
            "Missing ONNX inputs: "
            + ", ".join(
                sorted(missing_inputs)
            )
        )

    outputs = session.run(
        None,
        ort_inputs,
    )

    if not outputs:
        raise RuntimeError(
            "The ONNX model returned no output."
        )

    logits = np.asarray(outputs[0])

    if logits.ndim == 2:
        logits = logits[0]

    probabilities_array = softmax(
        logits
    )

    probabilities = []

    for class_id, score in enumerate(
        probabilities_array
    ):
        label = ID_TO_LABEL.get(
            class_id,
            f"label_{class_id}",
        )

        probabilities.append(
            {
                "label": label,
                "display_label": display_label(
                    label
                ),
                "score": float(score),
            }
        )

    probabilities.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    if not probabilities:
        raise RuntimeError(
            "The ONNX model returned "
            "no classification scores."
        )

    best = probabilities[0]

    return {
        "prediction": best["label"],
        "display_label": best[
            "display_label"
        ],
        "confidence": best["score"],
        "confidence_percent": round(
            best["score"] * 100,
            2,
        ),
        "model": MODEL_NAME,
        "model_id": MODEL_ID,
        "runtime": "ONNX Runtime CPU",
        "probabilities": probabilities,
    }
