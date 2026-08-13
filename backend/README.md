# Backend

The backend intentionally uses a lightweight Vercel Python Function as a secure proxy to Hugging Face Inference Providers.

## Why this design?

A full BERT + PyTorch runtime can make a serverless deployment much larger and slower. Keeping model weights on Hugging Face allows the Vercel deployment to stay small while still serving predictions from the team's fine-tuned BERT model.

## Required environment variables

- `HF_TOKEN`
- `HF_MODEL_ID`
- `HF_PROVIDER` (defaults to `hf-inference`)

The public frontend never sees `HF_TOKEN`.
