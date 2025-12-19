# import_text.py
import re
import unicodedata
from typing import Dict, List

# Mapping Politiscales FR -> variables internes
AXIS_LABEL_TO_VAR: Dict[str, str] = {
    "constructivisme": "constructivisme",
    "essentialisme": "essentialisme",

    "justice rehabilitative": "justice_rehabilitative",
    "justice réhabilitative": "justice_rehabilitative",

    "justice punitive": "justice_punitive",

    "progressisme": "progressisme",
    "conservatisme": "conservatisme",

    "internationalisme": "internationalisme",
    "nationalisme": "nationalisme",

    "communisme": "communisme",
    "capitalisme": "capitalisme",

    "regulation": "regulation",
    "régulation": "regulation",

    "laissez faire": "laissez_faire",
    "laissez-faire": "laissez_faire",

    "ecologie": "ecologie",
    "écologie": "ecologie",

    "productivisme": "productivisme",

    "revolution": "revolution",
    "révolution": "revolution",

    "reformisme": "reformisme",
    "réformisme": "reformisme",
}

VAR_NAMES: List[str] = [
    "constructivisme", "essentialisme",
    "justice_rehabilitative", "justice_punitive",
    "progressisme", "conservatisme",
    "internationalisme", "nationalisme",
    "communisme", "capitalisme",
    "regulation", "laissez_faire",
    "ecologie", "productivisme",
    "revolution", "reformisme",
]


def _normalize_text(s: str) -> str:
    """Minuscule + suppression des accents + réduction des espaces."""
    s = s.strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"\s+", " ", s)
    return s


def extract_scores_from_text(raw_text: str) -> Dict[str, int]:
    """
    Extrait les scores Politiscales à partir du texte brut
    (copier/coller de la page de résultats).

    Stratégie :
      - normalisation globale du texte
      - pour chaque label connu :
          chercher "<label> ... <nombre 0-100>"
          prendre le premier nombre 0..100 qui suit le label
    """
    scores: Dict[str, int] = {var: 0 for var in VAR_NAMES}

    norm_text = _normalize_text(raw_text)

    for label_raw, var_name in AXIS_LABEL_TO_VAR.items():
        label_norm = _normalize_text(label_raw)

        # On cherche le label dans le texte normalisé
        idx = norm_text.find(label_norm)
        if idx == -1:
            continue

        # On prend une tranche de texte après le label (80 caractères suffisent en pratique)
        segment = norm_text[idx : idx + 80]

        # On cherche des nombres dans cette tranche
        for m in re.findall(r"(\d{1,3})", segment):
            try:
                val = int(m)
            except ValueError:
                continue
            if 0 <= val <= 100:
                scores[var_name] = val
                break  # on prend le premier nombre après le label

    return scores
