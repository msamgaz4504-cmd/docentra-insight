FIELD_THRESHOLDS = {
    "event_titles": 0.55,
    "event_types": 0.65,
    "topics": 0.55,

    "speakers": 0.80,
    "organizers": 0.70,
    "organizations": 0.70,
    "partners": 0.70,
    "sponsors": 0.70,

    "venues": 0.65,
    "addresses": 0.65,
    "cities": 0.75,
    "countries": 0.75,

    "target_audiences": 0.60,
    "eligibility_requirements": 0.60,
    "participation_modes": 0.65,
}


def seuil(field):
    return FIELD_THRESHOLDS.get(
        field,
        0.50
    )


def supprimer_doublons(values):
    result = []
    seen = set()

    for value in values:
        value = value.strip()

        if not value:
            continue

        key = value.casefold()

        if key not in seen:
            seen.add(key)
            result.append(value)

    return result


def meilleur_candidat(
    candidates,
    min_score
):
    candidats_valides = [
        candidate
        for candidate in candidates
        if candidate["score"] >= min_score
    ]

    if not candidats_valides:
        return None, None

    meilleur = max(
        candidats_valides,
        key=lambda candidate: candidate["score"]
    )

    return (
        meilleur["value"],
        meilleur["score"]
    )


def tous_les_candidats(
    candidates,
    min_score
):
    candidats_valides = [
        candidate
        for candidate in candidates
        if candidate["score"] >= min_score
    ]

    candidats_valides.sort(
        key=lambda candidate: candidate["score"],
        reverse=True
    )

    values = [
        candidate["value"]
        for candidate in candidats_valides
    ]

    return supprimer_doublons(
        values
    )


def resoudre_champs(raw_data):
    event_title, event_title_score = meilleur_candidat(
        raw_data["event_titles"],
        seuil("event_titles")
    )

    event_type, event_type_score = meilleur_candidat(
        raw_data["event_types"],
        seuil("event_types")
    )

    venue, venue_score = meilleur_candidat(
        raw_data["venues"],
        seuil("venues")
    )

    address, address_score = meilleur_candidat(
        raw_data["addresses"],
        seuil("addresses")
    )

    city, city_score = meilleur_candidat(
        raw_data["cities"],
        seuil("cities")
    )

    country, country_score = meilleur_candidat(
        raw_data["countries"],
        seuil("countries")
    )

    participation_mode, participation_mode_score = meilleur_candidat(
        raw_data["participation_modes"],
        seuil("participation_modes")
    )

    return {
        "event_title": event_title,

        "event_type": event_type,

        "topics": tous_les_candidats(
            raw_data["topics"],
            seuil("topics")
        ),

        "speakers": tous_les_candidats(
            raw_data["speakers"],
            seuil("speakers")
        ),

        "organizers": tous_les_candidats(
            raw_data["organizers"],
            seuil("organizers")
        ),

        "organizations": tous_les_candidats(
            raw_data["organizations"],
            seuil("organizations")
        ),

        "partners": tous_les_candidats(
            raw_data["partners"],
            seuil("partners")
        ),

        "sponsors": tous_les_candidats(
            raw_data["sponsors"],
            seuil("sponsors")
        ),

        "venue": venue,

        "address": address,

        "city": city,

        "country": country,

        "target_audiences": tous_les_candidats(
            raw_data["target_audiences"],
            seuil("target_audiences")
        ),

        "eligibility_requirements": tous_les_candidats(
            raw_data["eligibility_requirements"],
            seuil("eligibility_requirements")
        ),

        "participation_mode": participation_mode,

        "event_dates": supprimer_doublons(
            raw_data["event_dates"]
        ),

        "registration_deadlines": supprimer_doublons(
            raw_data[
                "registration_deadlines"
            ]
        ),

        "times": supprimer_doublons(
            raw_data["times"]
        ),

        "emails": supprimer_doublons(
            raw_data["emails"]
        ),

        "phones": supprimer_doublons(
            raw_data["phones"]
        ),

        "urls": supprimer_doublons(
            raw_data["urls"]
        ),

        "confidence": {
            "event_title": event_title_score,
            "event_type": event_type_score,
            "venue": venue_score,
            "address": address_score,
            "city": city_score,
            "country": country_score,
            "participation_mode": participation_mode_score,
        }
    }