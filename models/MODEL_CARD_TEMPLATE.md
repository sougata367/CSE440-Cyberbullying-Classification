---
pipeline_tag: text-classification
language:
- en
library_name: transformers
tags:
- cyberbullying
- text-classification
- bert
- cse440
---

# CSE440 Cyberbullying BERT Classifier

Fine-tuned `bert-base-uncased` model for six-class English cyberbullying classification.

## Labels

- age
- ethnicity
- gender
- not_cyberbullying
- other_cyberbullying
- religion

## Evaluation

- Test accuracy: approximately 90.64%
- Test Macro-F1: approximately 0.897

## Intended use

Academic demonstration and research for the CSE440 project.

## Limitation

Model predictions can be wrong and should not be treated as final moderation, disciplinary, legal or safety decisions.
