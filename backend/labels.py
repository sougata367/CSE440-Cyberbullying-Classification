LABEL_META = {
    "age": {
        "display": "Age-based cyberbullying",
        "description": "The message targets a person or group based on age.",
    },
    "ethnicity": {
        "display": "Ethnicity-based cyberbullying",
        "description": "The message targets ethnicity, race or ethnic background.",
    },
    "gender": {
        "display": "Gender-based cyberbullying",
        "description": "The message targets a person or group based on gender.",
    },
    "not_cyberbullying": {
        "display": "Not cyberbullying",
        "description": "The model does not classify this text as cyberbullying.",
    },
    "other_cyberbullying": {
        "display": "Other cyberbullying",
        "description": "Cyberbullying is detected but it does not fit the named identity categories.",
    },
    "religion": {
        "display": "Religion-based cyberbullying",
        "description": "The message targets a person or group based on religion.",
    },
}

# Compatible with model outputs such as LABEL_0 as well as the id2label names.
ID_TO_LABEL = {
    0: "age",
    1: "ethnicity",
    2: "gender",
    3: "not_cyberbullying",
    4: "other_cyberbullying",
    5: "religion",
}

ALIASES = {
    "age": "age",
    "ethnicity": "ethnicity",
    "gender": "gender",
    "not_cyberbullying": "not_cyberbullying",
    "not-cyberbullying": "not_cyberbullying",
    "not cyberbullying": "not_cyberbullying",
    "other_cyberbullying": "other_cyberbullying",
    "other-cyberbullying": "other_cyberbullying",
    "other cyberbullying": "other_cyberbullying",
    "religion": "religion",
}

def canonicalize_label(raw_label: str) -> str:
    value = str(raw_label or "").strip()
    upper = value.upper()

    if upper.startswith("LABEL_"):
        try:
            return ID_TO_LABEL[int(upper.split("_", 1)[1])]
        except (ValueError, KeyError):
            pass

    normalized = value.lower().strip()
    return ALIASES.get(normalized, normalized.replace(" ", "_").replace("-", "_"))

def display_label(label: str) -> str:
    canonical = canonicalize_label(label)
    return LABEL_META.get(canonical, {}).get(
        "display",
        canonical.replace("_", " ").title(),
    )
