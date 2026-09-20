import hashlib
import html
import os
import tempfile
from pathlib import Path
from textwrap import dedent

import streamlit as st

from src.document_processing.extractor import extraire_document
from src.information_extraction.extractor import extraire_informations
from src.information_extraction.resolver import resoudre_champs
from src.question_answering.qa import repondre_question


st.set_page_config(
    page_title="Docentra Insight",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)


def render_html(content):
    st.html(
        dedent(content).strip()
    )


def charger_css():
    css_path = Path("assets/styles.css")

    if css_path.exists():
        st.html(css_path)


def initialiser_session():
    valeurs_initiales = {
        "analysis_results": None,
        "analyzed_file_hash": None,
        "analyzed_file_name": None,
        "qa_history": {},
    }

    for key, value in valeurs_initiales.items():
        if key not in st.session_state:
            st.session_state[key] = value


def calculer_hash(file_bytes):
    return hashlib.sha256(
        file_bytes
    ).hexdigest()


def valeur_affichable(value):
    if value is None:
        return "Not detected"

    if isinstance(value, list):
        if not value:
            return "Not detected"

        return ", ".join(
            str(item)
            for item in value
        )

    value = str(value).strip()

    if not value:
        return "Not detected"

    return value


def creer_card(label, value):
    value = valeur_affichable(
        value
    )

    label_safe = html.escape(
        str(label)
    )

    value_safe = html.escape(
        value
    )

    empty_class = ""

    if value == "Not detected":
        empty_class = " docentra-info-empty"

    return f"""
    <div class="docentra-info-card">
        <div class="docentra-info-label">
            {label_safe}
        </div>

        <div class="docentra-info-value{empty_class}">
            {value_safe}
        </div>
    </div>
    """


def afficher_grille(fields):
    cards = "".join(
        creer_card(
            label,
            value
        )
        for label, value in fields
    )

    render_html(
        f"""
        <div class="docentra-info-grid">
            {cards}
        </div>
        """
    )


def afficher_titre_section(
    title,
    description
):
    render_html(
        f"""
        <div class="docentra-section-heading">

            <h2>
                {html.escape(title)}
            </h2>

            <p>
                {html.escape(description)}
            </p>

        </div>
        """
    )


def analyser_fichier(
    file_bytes,
    file_name
):
    suffix = Path(
        file_name
    ).suffix.lower()

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_file.write(
                file_bytes
            )

            temp_path = temp_file.name

        pages = extraire_document(
            temp_path
        )

        results = []

        for page_data in pages:

            document_text = page_data[
                "text"
            ]

            raw_data = extraire_informations(
                document_text
            )

            structured_data = resoudre_champs(
                raw_data
            )

            results.append({
                "page": page_data["page"],
                "text": document_text,

                "source": page_data.get(
                    "source"
                ),

                "rotation": page_data.get(
                    "rotation",
                    0
                ),

                "structured_data": structured_data,
            })

        return results

    finally:

        if (
            temp_path
            and os.path.exists(temp_path)
        ):
            os.remove(
                temp_path
            )


def afficher_topbar():
    render_html(
        """
        <div class="docentra-topbar">

            <div class="docentra-brand">

                <div class="docentra-brand-mark">
                    D
                </div>

                <div class="docentra-brand-name">
                    Docentra Insight
                </div>

            </div>

        </div>
        """
    )


def afficher_hero():
    render_html(
        """
        <div class="docentra-hero">

            <h1 class="docentra-title">
                Turn documents into
                <span class="docentra-title-accent">
                    structured insight.
                </span>
            </h1>

            <p class="docentra-subtitle">
                Upload a document, extract key information,
                and explore its content through structured insights
                and intelligent question answering.
            </p>

        </div>
        """
    )

def afficher_upload():
    render_html(
        """
        <div class="docentra-surface-title">
            Analyze a document
        </div>

        <div class="docentra-surface-description">
            Upload a PDF, scanned document or event image.
            Supported formats: PDF, PNG, JPG and JPEG.
        </div>
        """
    )

    uploaded_file = st.file_uploader(
        "Upload document",
        type=[
            "pdf",
            "png",
            "jpg",
            "jpeg",
        ],
        label_visibility="collapsed",
    )

    return uploaded_file


def afficher_document_status(
    file_name,
    pages
):
    page_count = len(
        pages
    )

    render_html(
        f"""
        <div class="docentra-document-row">

            <div class="docentra-pill docentra-pill-success">
                Analysis complete
            </div>

            <div class="docentra-pill">
                {html.escape(file_name)}
            </div>

            <div class="docentra-pill">
                {page_count}
                page{"s" if page_count != 1 else ""}
            </div>

        </div>
        """
    )


def afficher_details_evenement(data):
    afficher_titre_section(
        "Event overview",
        "Core information detected from the selected page.",
    )

    afficher_grille([
        (
            "Event title",
            data.get("event_title")
        ),
        (
            "Event type",
            data.get("event_type")
        ),
        (
            "Topics",
            data.get("topics")
        ),
        (
            "Event date",
            data.get("event_dates")
        ),
        (
            "Registration deadline",
            data.get(
                "registration_deadlines"
            )
        ),
        (
            "Time",
            data.get("times")
        ),
        (
            "Participation mode",
            data.get(
                "participation_mode"
            )
        ),
    ])


def afficher_people(data):
    afficher_titre_section(
        "People & organizations",
        "Speakers, organizers and institutions identified in the document.",
    )

    afficher_grille([
        (
            "Speakers",
            data.get("speakers")
        ),
        (
            "Organizers",
            data.get("organizers")
        ),
        (
            "Organizations",
            data.get("organizations")
        ),
        (
            "Partners",
            data.get("partners")
        ),
        (
            "Sponsors",
            data.get("sponsors")
        ),
        (
            "Target audience",
            data.get(
                "target_audiences"
            )
        ),
        (
            "Eligibility",
            data.get(
                "eligibility_requirements"
            )
        ),
    ])


def afficher_localisation(data):
    afficher_titre_section(
        "Location",
        "Place and geographic information detected from the document.",
    )

    afficher_grille([
        (
            "Venue",
            data.get("venue")
        ),
        (
            "Address",
            data.get("address")
        ),
        (
            "City",
            data.get("city")
        ),
        (
            "Country",
            data.get("country")
        ),
    ])


def afficher_contact(data):
    afficher_titre_section(
        "Contact & access",
        "Detected contact details and online resources.",
    )

    afficher_grille([
        (
            "Email",
            data.get("emails")
        ),
        (
            "Phone",
            data.get("phones")
        ),
        (
            "Website",
            data.get("urls")
        ),
    ])


def afficher_historique(
    page_number
):
    history = st.session_state[
        "qa_history"
    ].get(
        page_number,
        []
    )

    if not history:
        return

    for message in history:

        question_safe = html.escape(
            message["question"]
        )

        answer_safe = html.escape(
            message["answer"]
        )

        render_html(
            f"""
            <div class="docentra-question-item">
                {question_safe}
            </div>

            <div class="docentra-answer">

                <div class="docentra-answer-label">
                    Answer
                </div>

                <p class="docentra-answer-text">
                    {answer_safe}
                </p>

            </div>
            """
        )


def afficher_qa(
    page_number,
    structured_data
):
    afficher_titre_section(
        "Ask the document",
        "Ask a question about the information extracted from this page.",
    )

    render_html(
        """
        <div class="docentra-chat-heading">

            <h2>
                What would you like to know?
            </h2>

            <p>
                Ask about the date, speaker, location,
                organization, deadline or other
                detected information.
            </p>

        </div>
        """
    )

    afficher_historique(
        page_number
    )

    question = st.chat_input(
        "Ask a question about this document..."
    )

    if question:

        answer = repondre_question(
            question,
            structured_data
        )

        if (
            page_number
            not in st.session_state[
                "qa_history"
            ]
        ):
            st.session_state[
                "qa_history"
            ][page_number] = []

        st.session_state[
            "qa_history"
        ][page_number].append({
            "question": question,
            "answer": answer,
        })

        st.rerun()


def main():
    charger_css()
    initialiser_session()

    afficher_topbar()
    afficher_hero()

    uploaded_file = afficher_upload()

    if uploaded_file is not None:

        file_bytes = uploaded_file.getvalue()

        file_hash = calculer_hash(
            file_bytes
        )

        if (
            st.session_state[
                "analyzed_file_hash"
            ]
            and
            st.session_state[
                "analyzed_file_hash"
            ] != file_hash
        ):
            st.session_state[
                "analysis_results"
            ] = None

            st.session_state[
                "analyzed_file_hash"
            ] = None

            st.session_state[
                "analyzed_file_name"
            ] = None

            st.session_state[
                "qa_history"
            ] = {}

        analyze_clicked = st.button(
            "Analyze document",
            use_container_width=True,
        )

        if analyze_clicked:

            try:

                with st.spinner(
                    "Analyzing document..."
                ):

                    results = analyser_fichier(
                        file_bytes,
                        uploaded_file.name
                    )

                st.session_state[
                    "analysis_results"
                ] = results

                st.session_state[
                    "analyzed_file_hash"
                ] = file_hash

                st.session_state[
                    "analyzed_file_name"
                ] = uploaded_file.name

                st.session_state[
                    "qa_history"
                ] = {}

                st.rerun()

            except ValueError as error:

                st.error(
                    str(error)
                )

            except Exception:

                st.error(
                    "The document could not be analyzed. "
                    "Please verify the file and try again."
                )

    results = st.session_state[
        "analysis_results"
    ]

    if not results:

        render_html(
            """
            <div class="docentra-footnote">
                Your document is processed locally by
                the Docentra analysis pipeline.
            </div>
            """
        )

        return

    afficher_document_status(
        st.session_state[
            "analyzed_file_name"
        ],
        results
    )

    if len(results) > 1:

        page_numbers = [
            result["page"]
            for result in results
        ]

        selected_page = st.selectbox(
            "Select page",
            options=page_numbers,
            format_func=lambda page:
                f"Page {page}",
        )

    else:

        selected_page = results[
            0
        ]["page"]

    selected_result = next(
        result
        for result in results
        if result["page"]
        == selected_page
    )

    structured_data = selected_result[
        "structured_data"
    ]

    afficher_details_evenement(
        structured_data
    )

    afficher_people(
        structured_data
    )

    afficher_localisation(
        structured_data
    )

    afficher_contact(
        structured_data
    )

    afficher_qa(
        selected_page,
        structured_data
    )

    render_html(
        """
        <div class="docentra-footnote">
            Docentra Insight · Structured intelligence
            from student documents and opportunities.
        </div>
        """
    )


if __name__ == "__main__":
    main()