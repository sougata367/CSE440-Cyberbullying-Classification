# CyberShield AI — Deployment Guide

This repository is arranged as a deployable React + Vercel Functions application.

## Architecture

```text
React UI (Vite)
      |
      | POST /api/predict
      v
Vercel Python Function
      |
      v
backend/inference.py
      |
      v
Hugging Face Inference Provider
      |
      v
Fine-tuned BERT Base model
```

The deployment intentionally keeps the Vercel backend lightweight. The fine-tuned BERT weights live in a Hugging Face model repository, while the Vercel API securely stores the Hugging Face token and calls the model.

## 1. Export the trained BERT model

Run the export snippet in `models/EXPORT_MODEL_TO_HF.md` at the end of the completed BERT training runtime.

The exported model must preserve this label order:

1. age
2. ethnicity
3. gender
4. not_cyberbullying
5. other_cyberbullying
6. religion

## 2. Set environment variables in Vercel

Create these project environment variables:

```text
HF_TOKEN=your_hugging_face_token
HF_MODEL_ID=your_username/cse440-cyberbullying-bert
HF_PROVIDER=hf-inference
```

Never put the real `HF_TOKEN` in GitHub.

## 3. Deploy

Import the GitHub repository into Vercel and deploy from the repository root.

Vercel will:

- install the React workspace
- build the Vite frontend
- deploy `api/*.py` as Python Functions
- serve `/api/predict` and `/api/health` on the same domain

## 4. Smoke tests

Health endpoint:

```text
GET /api/health
```

Prediction endpoint:

```text
POST /api/predict
Content-Type: application/json

{
  "text": "You are too old to understand social media."
}
```

A successful response has the shape:

```json
{
  "prediction": "age",
  "display_label": "Age-based cyberbullying",
  "confidence": 0.96,
  "confidence_percent": 96.0,
  "model": "BERT Base",
  "model_id": "your_username/cse440-cyberbullying-bert",
  "probabilities": []
}
```

## 5. Local frontend development

```bash
npm install
npm run dev
```

For end-to-end local Vercel routing, install Vercel CLI and use:

```bash
vercel dev
```

## Important

The current project notebook trains the final BERT model but does not automatically publish its trained weights. The model-export step is therefore required once, before the live classifier can return your actual trained-model predictions.
