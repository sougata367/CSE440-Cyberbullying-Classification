# Model Deployment Assets

The project benchmark selected **BERT Base** as the best model.

- Base checkpoint: `bert-base-uncased`
- Maximum token length: `64`
- Number of classes: `6`
- Test accuracy: approximately `0.9064`
- Test Macro-F1: approximately `0.8970`

## Why model weights are not committed here

The uploaded project notebook trains the model in Colab/runtime memory but does not contain a saved fine-tuned weight file. Also, BERT weights are large and are better stored in a model repository rather than normal GitHub source control.

Use `EXPORT_MODEL_TO_HF.md` once after training to publish the exact fine-tuned model and tokenizer to Hugging Face.

The Vercel backend then reads the model repository from:

```text
HF_MODEL_ID
```
