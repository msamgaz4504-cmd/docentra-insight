from src.question_answering.detector import detecter_intention
from src.question_answering.responder import construire_reponse


def repondre_question(question, structured_data):
    intent = detecter_intention(question)

    return construire_reponse(
        intent,
        structured_data
    )