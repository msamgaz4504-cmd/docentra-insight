from gliner import GLiNER


MODEL_NAME = "VAGOsolutions/SauerkrautLM-GLiNER"

model = GLiNER.from_pretrained(MODEL_NAME)


LABEL_TO_FIELD = {
    "event title": "event_titles",
    "event type": "event_types",
    "topic": "topics",

    "speaker": "speakers",
    "organizer": "organizers",
    "organization": "organizations",
    "partner": "partners",
    "sponsor": "sponsors",

    "venue": "venues",
    "address": "addresses",
    "city": "cities",
    "country": "countries",

    "target audience": "target_audiences",
    "eligibility requirement": "eligibility_requirements",
    "participation mode": "participation_modes",
}


LABELS = list(LABEL_TO_FIELD.keys())


def preparer_texte_ner(text):
    lignes = text.splitlines()
    lignes_utiles = []

    for ligne in lignes:
        ligne = ligne.strip()

        if len(ligne) < 2:
            continue

        if not any(char.isalpha() for char in ligne):
            continue

        lignes_utiles.append(ligne)

    return " ".join(lignes_utiles)


def ajouter_candidat(liste, value, score):
    value = value.strip()

    if not value:
        return

    for candidat in liste:
        if candidat["value"].casefold() == value.casefold():

            if score > candidat["score"]:
                candidat["score"] = score

            return

    liste.append({
        "value": value,
        "score": score
    })


def extraire_entites(text, threshold=0.50):
    texte_ner = preparer_texte_ner(text)

    entities = {
        field: []
        for field in LABEL_TO_FIELD.values()
    }

    if not texte_ner:
        return entities

    results = model.predict_entities(
        texte_ner,
        LABELS,
        threshold=threshold
    )

    for result in results:
        label = result["label"]

        if label not in LABEL_TO_FIELD:
            continue

        field = LABEL_TO_FIELD[label]
        value = result["text"].strip()
        score = round(float(result["score"]), 4)

        ajouter_candidat(
            entities[field],
            value,
            score
        )

    return entities