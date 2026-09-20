# Docentra Insight

Docentra Insight est une application locale d’intelligence documentaire conçue pour transformer des documents PDF ou image en informations structurées et interrogeables.

L’application combine extraction de texte, OCR, expressions régulières, reconnaissance d’entités avec GLiNER et un module de questions-réponses basé sur des règles.

## Fonctionnalités

- Support des fichiers PDF, PNG, JPG et JPEG
- Extraction directe du texte pour les PDF natifs
- OCR pour les PDF scannés et les images
- Détection et correction de l’orientation
- Extraction structurée d’informations
- Validation des dates et données à format déterministe
- Reconnaissance d’entités avec GLiNER
- Résolution des candidats selon leur score de confiance
- Traitement indépendant des différentes pages d’un document
- Questions-réponses à partir des informations extraites
- Interface web avec Streamlit

## Pipeline

```text
Document
   ↓
Extraction de texte / OCR
   ↓
Prétraitement
   ↓
Regex + GLiNER
   ↓
Résolution des champs
   ↓
Structured Data
   ↓
Question Answering
```

Les expressions régulières sont principalement utilisées pour les informations possédant une structure identifiable, notamment :

```text
dates
heures
emails
téléphones
URLs
```

GLiNER est utilisé pour extraire les informations sémantiques telles que les sujets, intervenants, organisations, lieux et autres entités présentes dans le document.

Un resolver filtre ensuite les candidats et produit une représentation structurée exploitable par l’application.

## Questions-réponses

Le module de questions-réponses est actuellement basé sur des intentions prédéfinies.

```text
Question utilisateur
        ↓
Normalisation
        ↓
Détection de l’intention
        ↓
Recherche dans les données structurées
        ↓
Construction de la réponse
```

Les réponses sont construites uniquement à partir des informations extraites du document.

La version actuelle n’utilise ni API LLM externe ni pipeline RAG.

## Architecture

```text
docentra-insight/
├── app.py
├── assets/
│   └── styles.css
├── src/
│   ├── document_processing/
│   ├── information_extraction/
│   ├── question_answering/
│   └── utils/
├── requirements.txt
├── .gitignore
└── README.md
```

## Technologies

- Python
- Streamlit
- PyMuPDF
- Tesseract OCR
- pytesseract
- Pillow
- GLiNER
- PyTorch
- Hugging Face Transformers
- Regular Expressions

Le modèle utilisé actuellement pour l’extraction sémantique est :

```text
VAGOsolutions/SauerkrautLM-GLiNER
```

## Installation

Créer un environnement virtuel :

```bash
python -m venv .venv
```

Sous Windows PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Tesseract OCR doit également être installé sur le système.

Vérifier son installation :

```bash
tesseract --version
```

Le pipeline OCR utilise actuellement le français et l’anglais :

```text
fra+eng
```

## Lancement

Depuis la racine du projet :

```bash
streamlit run app.py
```

Si le watcher Streamlit génère des avertissements liés aux modules Transformers :

```bash
streamlit run app.py --server.fileWatcherType none
```

L’application permet ensuite d’importer un document, de lancer son analyse, de consulter les informations détectées et d’interroger la page sélectionnée.

## Limites actuelles

La qualité de l’extraction dépend de la qualité du document source. Les documents très graphiques, déformés ou de faible résolution peuvent générer des erreurs OCR qui affectent ensuite l’extraction des entités.

La reconnaissance des questions repose actuellement sur des intentions et des formulations prédéfinies. Une formulation non couverte par ces règles peut donc ne pas être reconnue.

Lorsqu’une information n’est pas détectée avec suffisamment de fiabilité, l’application privilégie une valeur absente plutôt que d’inventer une réponse.

## Auteur

**Meryem Samgaz**  
Data Engineering and Artificial Intelligence Engineering Student — ENSA Safi
