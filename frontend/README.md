# Frontend

Premium React + Vite interface for the CSE440 cyberbullying classifier.

## Main interaction

1. User writes or pastes a message.
2. Frontend sends `{ "text": "..." }` to `/api/predict`.
3. The result card displays:
   - predicted class
   - confidence
   - class probabilities
   - model name

The UI is responsive and uses only React + CSS, keeping the deployment lightweight.
