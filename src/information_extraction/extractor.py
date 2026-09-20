from src.information_extraction.ner import extraire_entites
from src.information_extraction.regex_resolver import resoudre_regex


def extraire_informations(document_text):
    regex_data = resoudre_regex(
        document_text
    )

    entites = extraire_entites(
        document_text
    )

    return {
        "event_dates": regex_data[
            "event_dates"
        ],
        "registration_deadlines": regex_data[
            "registration_deadlines"
        ],
        "times": regex_data[
            "times"
        ],
        "emails": regex_data[
            "emails"
        ],
        "phones": regex_data[
            "phones"
        ],
        "urls": regex_data[
            "urls"
        ],

        "event_titles": entites[
            "event_titles"
        ],
        "event_types": entites[
            "event_types"
        ],
        "topics": entites[
            "topics"
        ],

        "speakers": entites[
            "speakers"
        ],
        "organizers": entites[
            "organizers"
        ],
        "organizations": entites[
            "organizations"
        ],
        "partners": entites[
            "partners"
        ],
        "sponsors": entites[
            "sponsors"
        ],

        "venues": entites[
            "venues"
        ],
        "addresses": entites[
            "addresses"
        ],
        "cities": entites[
            "cities"
        ],
        "countries": entites[
            "countries"
        ],

        "target_audiences": entites[
            "target_audiences"
        ],
        "eligibility_requirements": entites[
            "eligibility_requirements"
        ],
        "participation_modes": entites[
            "participation_modes"
        ],
    }