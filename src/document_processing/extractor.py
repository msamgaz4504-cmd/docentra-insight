from pathlib import Path

import pymupdf
from PIL import Image, UnidentifiedImageError

from src.document_processing.ocr import (
    extraire_texte_ocr,
    extraire_texte_image,
)
from src.document_processing.preprocessing import nettoyer_texte
from src.utils.validators import texte_suffisant


SUPPORTED_IMAGE_FORMATS = {
    ".png",
    ".jpg",
    ".jpeg",
}

SUPPORTED_FORMATS = {
    ".pdf",
    *SUPPORTED_IMAGE_FORMATS,
}


def construire_page(
    page_number,
    text,
    source,
    rotation=0,
    ocr_data=None,
):
    clean_text = nettoyer_texte(text)

    return {
        "page": page_number,
        "text": clean_text,
        "source": source,
        "rotation": rotation,
        "ocr_data": ocr_data,
    }


def extraire_pages_pdf(pdf_path):
    pages = []

    try:
        document = pymupdf.open(pdf_path)

    except Exception as error:
        raise ValueError(
            "Unable to open the PDF document."
        ) from error

    try:
        if document.page_count == 0:
            raise ValueError(
                "The PDF does not contain any pages."
            )

        for page_number, page in enumerate(
            document,
            start=1,
        ):
            text = page.get_text()

            if texte_suffisant(text):
                page_data = construire_page(
                    page_number=page_number,
                    text=text,
                    source="native_pdf",
                )

            else:
                try:
                    ocr_result = extraire_texte_ocr(
                        page
                    )

                except Exception as error:
                    raise ValueError(
                        f"OCR failed on page {page_number}."
                    ) from error

                page_data = construire_page(
                    page_number=page_number,
                    text=ocr_result["text"],
                    source="ocr",
                    rotation=ocr_result.get(
                        "rotation",
                        0,
                    ),
                    ocr_data=ocr_result.get(
                        "data"
                    ),
                )

            pages.append(
                page_data
            )

    finally:
        document.close()

    if not any(
        page["text"].strip()
        for page in pages
    ):
        raise ValueError(
            "No usable text could be extracted from this document."
        )

    return pages


def extraire_image(image_path):
    try:
        with Image.open(image_path) as image:
            ocr_result = extraire_texte_image(
                image
            )

    except UnidentifiedImageError as error:
        raise ValueError(
            "The uploaded image could not be read."
        ) from error

    except Exception as error:
        raise ValueError(
            "OCR failed while processing the image."
        ) from error

    page_data = construire_page(
        page_number=1,
        text=ocr_result["text"],
        source="image_ocr",
        rotation=ocr_result.get(
            "rotation",
            0,
        ),
        ocr_data=ocr_result.get(
            "data"
        ),
    )

    if not page_data["text"].strip():
        raise ValueError(
            "No usable text could be extracted from this image."
        )

    return [
        page_data
    ]


def extraire_document(file_path):
    path = Path(file_path)

    if not path.exists():
        raise ValueError(
            "The document could not be found."
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_FORMATS:
        raise ValueError(
            "Unsupported file format. "
            "Please upload a PDF, PNG, JPG or JPEG file."
        )

    if extension == ".pdf":
        return extraire_pages_pdf(
            file_path
        )

    return extraire_image(
        file_path
    )