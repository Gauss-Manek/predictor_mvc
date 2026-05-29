def predict_sentiment(text: str) -> dict:
    clean_text = text.lower()
    if any(word in clean_text for word in ["bon", "super", "excellent", "génial", "magnifique"]):
        return {"sentiment": "positif", "score": 0.92}
    elif any(word in clean_text for word in ["mauvais", "nul", "horrible", "erreur", "casse"]):
        return {"sentiment": "négatif", "score": 0.88}
    else:
        return {"sentiment": "neutre", "score": 0.50}