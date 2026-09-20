import re
import unicodedata

from src.question_answering.intents import INTENTS


def normaliser_question(question):
    question = question.casefold()

    question = unicodedata.normalize(
        "NFD",
        question
    )

    question = "".join(
        char
        for char in question
        if unicodedata.category(char) != "Mn"
    )

    question = re.sub(
        r"\s+",
        " ",
        question
    )

    return question.strip()


def detecter_intention(question):
    question = normaliser_question(
        question
    )

    for intent, patterns in INTENTS.items():

        for pattern in patterns:

            if re.search(
                pattern,
                question
            ):
                return intent

    return None
