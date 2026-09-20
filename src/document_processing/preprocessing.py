import re


def nettoyer_texte(final_text):

    text = final_text.strip()

    lines = text.splitlines()

    clean_lines = []

    for line in lines:

        line = line.strip()

        line = re.sub(r"[ \t]+", " ", line)

        if line:
            clean_lines.append(line)

    return "\n".join(clean_lines)