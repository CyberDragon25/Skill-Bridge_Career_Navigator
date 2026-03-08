
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


def _build_training_examples(jobs: List[Dict]):
    texts = []
    labels = []

    for job in jobs:
        title = job.get("title", "")
        role = job.get("role", "")
        description = job.get("description", "")
        required = " ".join(job.get("required_skills", []))
        nice = " ".join(job.get("nice_to_have_skills", []))

        text = f"{title} {description} {required} {nice}".strip()
        if text and role:
            texts.append(text)
            labels.append(role)

    return texts, labels


def train_role_classifier(jobs: List[Dict]):
    texts, labels = _build_training_examples(jobs)

    if len(set(labels)) < 2:
        return None, None

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=3000
    )

    X = vectorizer.fit_transform(texts)
    model = LogisticRegression(max_iter=1000)
    model.fit(X, labels)

    return vectorizer, model


def predict_role_fit(resume_text: str, jobs: List[Dict]) -> Dict:
    vectorizer, model = train_role_classifier(jobs)

    if vectorizer is None or model is None or not resume_text.strip():
        return {
            "predicted_role": "Unavailable",
            "confidence": 0.0,
            "top_roles": []
        }

    X_resume = vectorizer.transform([resume_text])
    probs = model.predict_proba(X_resume)[0]
    classes = model.classes_

    ranked = sorted(
        [{"role": role, "probability": round(float(prob), 4)} for role, prob in zip(classes, probs)],
        key=lambda x: x["probability"],
        reverse=True
    )

    top = ranked[:3]

    return {
        "predicted_role": top[0]["role"] if top else "Unavailable",
        "confidence": round(top[0]["probability"] * 100, 1) if top else 0.0,
        "top_roles": top
    }