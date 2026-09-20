LABELS = {
    "event_title": "Titre",
    "event_type": "Type d'événement",
    "topics": "Sujet",
    "speakers": "Intervenant(s)",
    "organizers": "Organisateur(s)",
    "organizations": "Organisation(s)",
    "partners": "Partenaire(s)",
    "sponsors": "Sponsor(s)",
    "event_dates": "Date",
    "registration_deadlines": "Date limite d'inscription",
    "times": "Horaire",
    "target_audiences": "Public cible",
    "eligibility_requirements": "Conditions",
    "participation_mode": "Mode de participation",
    "emails": "Email",
    "phones": "Téléphone",
    "urls": "Lien",
}


def valeur_disponible(value):
    return value not in (
        None,
        "",
        [],
        {}
    )


def joindre_valeurs(values):
    return ", ".join(values)


def construire_localisation(structured_data):
    location_parts = []

    for field in [
        "venue",
        "address",
        "city",
        "country"
    ]:
        value = structured_data.get(field)

        if valeur_disponible(value):
            location_parts.append(value)

    if not location_parts:
        return "Cette information n'a pas été détectée dans le document."

    return "Lieu : " + ", ".join(location_parts)


def construire_reponse(intent, structured_data):
    if intent is None:
        return "Je n'ai pas compris la question."

    if intent == "location":
        return construire_localisation(
            structured_data
        )

    value = structured_data.get(intent)

    if not valeur_disponible(value):
        return "Cette information n'a pas été détectée dans le document."

    if isinstance(value, list):
        value = joindre_valeurs(value)

    label = LABELS.get(
        intent,
        intent
    )

    return f"{label} : {value}"