import os
import shutil
import urllib.request
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

from backend.config import HF_TOKEN, MODEL_ID, MODEL_NAME
from backend.labels import ID_TO_LABEL, display_label


# =========================================================
# SETTINGS
# =========================================================

MAX_LENGTH = 64

MODEL_SUBFOLDER = "onnx-int8"
ONNX_FILENAME = "model_quantized.onnx"
TOKENIZER_FILENAME = "tokenizer.json"

CACHE_DIR = Path("/tmp/cse440_onnx_int8")

MODEL_PATH = CACHE_DIR / ONNX_FILENAME
TOKENIZER_PATH = CACHE_DIR / TOKENIZER_FILENAME


class ModelConfigurationError(RuntimeError):
    pass


# =========================================================
# DOWNLOAD FILE DIRECTLY FROM HUGGING FACE
# =========================================================

def _download_hf_file(remote_path: str, local_path: Path):
    encoded_path = quote(remote_path, safe="/")

    url = (
        f"https://huggingface.co/"
        f"{MODEL_ID}/resolve/main/"
        f"{encoded_path}"
    )

    headers = {
        "User-Agent": "CSE440-Cyberbullying-Classifier/1.0"
    }

    # Token is optional because the current model repo is public.
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    request = urllib.request.Request(
        url,
        headers=headers,
    )

    temp_path = Path(str(local_path) + ".part")

    try:
        with urllib.request.urlopen(
            request,
            timeout=60,
        ) as response:
            with open(temp_path, "wb") as output_file:
                shutil.copyfileobj(
                    response,
                    output_file,
                    length=1024 * 1024,
                )

        os.replace(
            temp_path,
            local_path,
        )

    except Exception:
        if temp_path.exists():
            temp_path.unlink()

        raise


# =========================================================
# PREPARE MODEL FILES
# =========================================================

@lru_cache(maxsize=1)
def prepare_model_files():
    if not MODEL_ID:
        raise ModelConfigurationError(
            "HF_MODEL_ID is not configured on the server."
        )

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not MODEL_PATH.exists():
        print("Downloading ONNX model...")

        _download_hf_file(
            f"{MODEL_SUBFOLDER}/{ONNX_FILENAME}",
            MODEL_PATH,
        )

    if not TOKENIZER_PATH.exists():
        print("Downloading tokenizer...")

        _download_hf_file(
            f"{MODEL_SUBFOLDER}/{TOKENIZER_FILENAME}",
            TOKENIZER_PATH,
        )

    if not MODEL_PATH.exists():
        raise RuntimeError(
            "ONNX model download failed."
        )

    if not TOKENIZER_PATH.exists():
        raise RuntimeError(
            "Tokenizer download failed."
        )

    return True


# =========================================================
# LOAD TOKENIZER
# =========================================================

@lru_cache(maxsize=1)
def get_tokenizer():
    prepare_model_files()

    tokenizer = Tokenizer.from_file(
        str(TOKENIZER_PATH)
    )

    tokenizer.enable_truncation(
        max_length=MAX_LENGTH
    )

    return tokenizer


# =========================================================
# LOAD ONNX MODEL
# =========================================================

@lru_cache(maxsize=1)
def get_session():
    prepare_model_files()

    session_options = ort.SessionOptions()

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


# =========================================================
# SOFTMAX
# =========================================================

def softmax(values):
    values = np.asarray(
        values,
        dtype=np.float64,
    )

    values = values - np.max(values)

    exp_values = np.exp(values)

    return exp_values / np.sum(exp_values)


# =========================================================
# CLASSIFY TEXT
# =========================================================

def classify_text(text: str):
    tokenizer = get_tokenizer()
    session = get_session()

    encoding = tokenizer.encode(
        text
    )

    available_inputs = {
        "input_ids": np.asarray(
            [encoding.ids],
            dtype=np.int64,
        ),
        "attention_mask": np.asarray(
            [encoding.attention_mask],
            dtype=np.int64,
        ),
        "token_type_ids": np.asarray(
            [encoding.type_ids],
            dtype=np.int64,
        ),
    }

    model_input_names = {
        item.name
        for item in session.get_inputs()
    }

    ort_inputs = {}

    for input_name in model_input_names:
        if input_name not in available_inputs:
            raise RuntimeError(
                f"Unsupported ONNX input: {input_name}"
            )

        ort_inputs[input_name] = (
            available_inputs[input_name]
        )

    outputs = session.run(
        None,
        ort_inputs,
    )

    if not outputs:
        raise RuntimeError(
            "The ONNX model returned no output."
        )

    logits = np.asarray(
        outputs[0]
    )

    if logits.ndim == 2:
        logits = logits[0]

    scores = softmax(
        logits
    )

    probabilities = []

    for class_id, score in enumerate(scores):
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
            "The model returned no classification scores."
        )

    best = probabilities[0]

    return {
        "prediction": best["label"],
        "display_label": best["display_label"],
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
