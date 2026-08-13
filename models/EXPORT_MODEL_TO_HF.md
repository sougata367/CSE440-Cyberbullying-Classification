# Export the Fine-Tuned BERT Model to Hugging Face

Run this **at the end of the same Colab runtime where `final_bert_trainer`, `bert_tokenizer` and `label_encoder` already exist**.

## Step 1 — Install/login

```python
!pip -q install -U huggingface_hub
from huggingface_hub import login

login()
```

Paste a Hugging Face write token when Colab asks for it.

## Step 2 — Verify the exact class order

```python
print(dict(enumerate(label_encoder.classes_)))
```

Expected order:

```python
{
    0: "age",
    1: "ethnicity",
    2: "gender",
    3: "not_cyberbullying",
    4: "other_cyberbullying",
    5: "religion"
}
```

## Step 3 — Preserve label metadata and save locally

```python
export_dir = "/content/cse440-cyberbullying-bert"

id2label = {
    index: label
    for index, label in enumerate(label_encoder.classes_)
}
label2id = {
    label: index
    for index, label in enumerate(label_encoder.classes_)
}

trained_model = final_bert_trainer.model
trained_model.config.id2label = id2label
trained_model.config.label2id = label2id

final_bert_trainer.save_model(export_dir)
bert_tokenizer.save_pretrained(export_dir)

print("Saved model to:", export_dir)
```

## Step 4 — Push model + tokenizer to Hugging Face

Change the repo ID to your own Hugging Face username.

```python
HF_REPO_ID = "YOUR_HF_USERNAME/cse440-cyberbullying-bert"

trained_model.push_to_hub(HF_REPO_ID)
bert_tokenizer.push_to_hub(HF_REPO_ID)

print("Published:", HF_REPO_ID)
```

## Step 5 — Configure Vercel

Add the following environment variables to the Vercel project:

```text
HF_TOKEN=your_hugging_face_token
HF_MODEL_ID=YOUR_HF_USERNAME/cse440-cyberbullying-bert
HF_PROVIDER=hf-inference
```

Do not commit your real `HF_TOKEN` to GitHub.
