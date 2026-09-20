import io

from PIL import Image, ImageOps
import pytesseract
from pytesseract import Output

def page_vers_image(page, dpi=300):
    pix = page.get_pixmap(
        dpi=dpi,
        alpha=False
    )

    return Image.open(
        io.BytesIO(pix.tobytes("png"))
    )

def calculer_score_ocr(data):
    
    confidences = []

    mots_valides = 0

    for index, word in enumerate(data["text"]):

        word = word.strip()

        if not word:
            continue

        try:
            confidence = float(data["conf"][index])
        except (ValueError, TypeError):
            continue

        if confidence >= 0:
            confidences.append(confidence)
            mots_valides += 1

    if not confidences:
        return 0

    moyenne = sum(confidences) / len(confidences)

    return moyenne + min(mots_valides, 50) * 0.2

def detecter_rotation_image(image):
    try:
        osd = pytesseract.image_to_osd(
            image,
            output_type=Output.DICT
        )

        return int(osd.get("rotate", 0))

    except pytesseract.TesseractError:
        return 0


def preparer_image_ocr(image):
    image = ImageOps.exif_transpose(image)

    if image.mode != "RGB":
        image = image.convert("RGB")

    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image)

    return image


def data_vers_texte(data, min_confidence=20):
    lignes = {}

    for index, word in enumerate(data["text"]):

        word = word.strip()

        if not word:
            continue

        try:
            confidence = float(data["conf"][index])
        except (ValueError, TypeError):
            confidence = -1

        if confidence < min_confidence:
            continue

        key = (
            data["block_num"][index],
            data["par_num"][index],
            data["line_num"][index],
        )

        lignes.setdefault(key, [])
        lignes[key].append(word)

    return "\n".join(
        " ".join(words)
        for words in lignes.values()
    )


def extraire_texte_image(
    image,
    language="fra+eng"
):

    image = ImageOps.exif_transpose(image)

    rotation = detecter_rotation_image(image)

    if rotation != 0:
        image = image.rotate(
            -rotation,
            expand=True
        )

    image = preparer_image_ocr(image)

    candidats = []

    for psm in [6, 11]:

        data = pytesseract.image_to_data(
            image,
            lang=language,
            config=f"--psm {psm}",
            output_type=Output.DICT
        )

        text = data_vers_texte(data)

        score = calculer_score_ocr(data)

        candidats.append({
            "text": text,
            "data": data,
            "score": score,
            "psm": psm
        })

    meilleur = max(
        candidats,
        key=lambda candidat: candidat["score"]
    )

    return {
        "text": meilleur["text"],
        "rotation": rotation,
        "data": meilleur["data"],
        "ocr_score": meilleur["score"],
        "psm": meilleur["psm"]
    }

def extraire_texte_ocr(
    page,
    language="fra+eng",
    dpi=300
):
    image = page_vers_image(
        page,
        dpi=dpi
    )

    return extraire_texte_image(
        image,
        language=language
    )