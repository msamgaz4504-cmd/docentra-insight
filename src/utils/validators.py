def texte_suffisant(text, min_length=10):
    text = text.strip()
    return len(text) >= min_length