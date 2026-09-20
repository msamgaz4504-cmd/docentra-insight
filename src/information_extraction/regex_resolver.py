import re
from datetime import datetime


MONTHS = {
    "janvier": 1,
    "january": 1,
    "février": 2,
    "fevrier": 2,
    "february": 2,
    "mars": 3,
    "march": 3,
    "avril": 4,
    "april": 4,
    "mai": 5,
    "may": 5,
    "juin": 6,
    "june": 6,
    "juillet": 7,
    "july": 7,
    "août": 8,
    "aout": 8,
    "august": 8,
    "septembre": 9,
    "september": 9,
    "octobre": 10,
    "october": 10,
    "novembre": 11,
    "november": 11,
    "décembre": 12,
    "decembre": 12,
    "december": 12,
}


MONTH_PATTERN = "|".join(
    sorted(
        map(re.escape, MONTHS.keys()),
        key=len,
        reverse=True
    )
)


NUMERIC_DATE_PATTERN = (
    r"\b(?:0?[1-9]|[12]\d|3[01])"
    r"[/-]"
    r"(?:0?[1-9]|1[0-2])"
    r"[/-]"
    r"\d{4}\b"
)


ISO_DATE_PATTERN = (
    r"\b\d{4}-"
    r"(?:0?[1-9]|1[0-2])-"
    r"(?:0?[1-9]|[12]\d|3[01])\b"
)


TEXT_DATE_PATTERN = (
    rf"\b(?:0?[1-9]|[12]\d|3[01])"
    rf"\s+(?:{MONTH_PATTERN})"
    rf"\s+\d{{4}}\b"
)


DATE_PATTERN = (
    rf"(?:{TEXT_DATE_PATTERN}|"
    rf"{NUMERIC_DATE_PATTERN}|"
    rf"{ISO_DATE_PATTERN})"
)


TIME_PATTERN = (
    r"\b(?:[01]?\d|2[0-3])"
    r"\s*(?:h|:)\s*"
    r"[0-5]\d\b"
)


EMAIL_PATTERN = (
    r"\b[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+"
    r"\.[A-Za-z]{2,}\b"
)


URL_PATTERN = (
    r"(?:https?://|www\.)[^\s<>'\"]+"
    r"|"
    r"(?<!@)\b"
    r"(?:[A-Za-z0-9-]+\.)+"
    r"[A-Za-z]{2,}"
    r"(?:/[^\s<>'\"]*)?"
)


PHONE_PATTERN = (
    r"(?<!\w)"
    r"\+?\d"
    r"(?:[\s().-]?\d){7,14}"
    r"(?!\w)"
)


DEADLINE_WORDS = [
    "deadline",
    "date limite",
    "limite d'inscription",
    "limite des inscriptions",
    "inscription avant",
    "inscriptions avant",
    "inscription jusqu",
    "inscriptions jusqu",
    "registration deadline",
    "application deadline",
    "apply before",
    "register before",
    "register by",
    "applications close",
]


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


def date_valide(value):
    value = value.strip()

    if re.fullmatch(NUMERIC_DATE_PATTERN, value):
        separator = "/" if "/" in value else "-"
        day, month, year = value.split(separator)

        try:
            datetime(
                int(year),
                int(month),
                int(day)
            )
            return True
        except ValueError:
            return False

    if re.fullmatch(ISO_DATE_PATTERN, value):
        year, month, day = value.split("-")

        try:
            datetime(
                int(year),
                int(month),
                int(day)
            )
            return True
        except ValueError:
            return False

    match = re.fullmatch(
        rf"(\d{{1,2}})\s+({MONTH_PATTERN})\s+(\d{{4}})",
        value,
        flags=re.IGNORECASE
    )

    if match:
        day = int(match.group(1))
        month_name = match.group(2).casefold()
        year = int(match.group(3))

        month = MONTHS.get(month_name)

        if month is None:
            return False

        try:
            datetime(year, month, day)
            return True
        except ValueError:
            return False

    return False


def normaliser_heure(value):
    value = value.lower().strip()

    value = re.sub(
        r"\s+",
        "",
        value
    )

    value = value.replace(
        "h",
        ":"
    )

    hour, minute = value.split(":")

    return f"{int(hour):02d}:{minute}"


def nettoyer_url(value):
    return value.rstrip(
        ".,;:!?)]}"
    )


def telephone_valide(value):
    digits = re.sub(
        r"\D",
        "",
        value
    )

    return 8 <= len(digits) <= 15


def contient_contexte_deadline(line):
    line = line.casefold()

    return any(
        keyword.casefold() in line
        for keyword in DEADLINE_WORDS
    )


def extraire_dates(text):
    event_dates = []
    registration_deadlines = []

    for line in text.splitlines():
        matches = re.findall(
            DATE_PATTERN,
            line,
            flags=re.IGNORECASE
        )

        if not matches:
            continue

        deadline_context = contient_contexte_deadline(
            line
        )

        for value in matches:
            value = value.strip()

            if not date_valide(value):
                continue

            if deadline_context:
                registration_deadlines.append(value)
            else:
                event_dates.append(value)

    return {
        "event_dates": supprimer_doublons(
            event_dates
        ),
        "registration_deadlines": supprimer_doublons(
            registration_deadlines
        )
    }


def extraire_heures(text):
    matches = re.findall(
        TIME_PATTERN,
        text,
        flags=re.IGNORECASE
    )

    return supprimer_doublons([
        normaliser_heure(value)
        for value in matches
    ])


def extraire_emails(text):
    return supprimer_doublons(
        re.findall(
            EMAIL_PATTERN,
            text
        )
    )


def extraire_urls(text):
    matches = re.findall(
        URL_PATTERN,
        text,
        flags=re.IGNORECASE
    )

    return supprimer_doublons([
        nettoyer_url(value)
        for value in matches
    ])


def extraire_telephones(text):
    matches = re.findall(
        PHONE_PATTERN,
        text
    )

    values = []

    for value in matches:
        value = value.strip()

        if telephone_valide(value):
            values.append(value)

    return supprimer_doublons(values)


def resoudre_regex(text):
    dates = extraire_dates(text)

    return {
        "event_dates": dates[
            "event_dates"
        ],
        "registration_deadlines": dates[
            "registration_deadlines"
        ],
        "times": extraire_heures(text),
        "emails": extraire_emails(text),
        "phones": extraire_telephones(text),
        "urls": extraire_urls(text),
    }