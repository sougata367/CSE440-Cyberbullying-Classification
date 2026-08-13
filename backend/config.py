import os

MODEL_ID = os.getenv("HF_MODEL_ID", "").strip()
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
HF_PROVIDER = os.getenv("HF_PROVIDER", "hf-inference").strip() or "hf-inference"

MODEL_NAME = "BERT Base"
MODEL_ACCURACY = 0.9064
MODEL_MACRO_F1 = 0.8970

MAX_INPUT_CHARS = 2000
MIN_INPUT_CHARS = 3
