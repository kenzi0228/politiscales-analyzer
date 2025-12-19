from __future__ import annotations

"""
ocr.py
------
Extraction des 16 scores Politiscales directement depuis une capture d'écran
en analysant la longueur des barres de couleur, sans dépendre de Tesseract.

Principe :
- On détecte les grandes bandes de couleur horizontales (les 8 axes).
- Pour chaque bande, on détecte les segments colorés à gauche et à droite.
- La longueur relative des segments permet de reconstituer les pourcentages
  gauche / centre (gris) / droite, normalisés pour sommer à 100.
"""

from typing import Dict, Tuple, List

import numpy as np
from PIL import Image


# Paramètres ajustables si besoin
X_START_FRAC = 0.10   # portion gauche de l'image à ignorer (logo, libellés)
X_END_FRAC   = 0.95   # portion droite de l'image conservée
SAT_THRESHOLD = 70    # seuil de saturation (0..255) pour considérer un pixel "coloré"
VAL_THRESHOLD = 80    # seuil de luminosité (0..255)
MIN_STRIPE_HEIGHT = 5
MAX_STRIPE_HEIGHT = 60
MIN_SEGMENT_WIDTH = 10  # largeur min d'un segment horizontal pour être significatif


# Ordre des axes tel qu'affiché par Politiscales (de haut en bas)
AXIS_ORDER: List[Tuple[str, str]] = [
    ("constructivisme", "essentialisme"),
    ("justice_rehabilitative", "justice_punitive"),
    ("progressisme", "conservatisme"),
    ("internationalisme", "nationalisme"),
    ("communisme", "capitalisme"),
    ("regulation", "laissez_faire"),
    ("ecologie", "productivisme"),
    ("revolution", "reformisme"),
]


def _find_color_stripes(mask: np.ndarray) -> List[Tuple[int, int]]:
    """
    À partir d'un masque binaire (H x W) indiquant les pixels "colorés"
    dans la zone centrale de l'image, repère les bandes horizontales
    où se situent les barres des axes.

    Retourne une liste de couples (y_debut, y_fin) triés par y croissant.
    """
    h, w = mask.shape
    row_color = mask.any(axis=1)  # True si au moins un pixel coloré sur la ligne

    stripes: List[Tuple[int, int]] = []
    start = None
    for y, has_color in enumerate(row_color):
        if has_color and start is None:
            start = y
        elif not has_color and start is not None:
            stripes.append((start, y - 1))
            start = None
    if start is not None:
        stripes.append((start, h - 1))

    # garder les bandes plausibles (hauteur dans [MIN, MAX]) et sous la bannière/haut de page
    filtered: List[Tuple[int, int]] = []
    for (y0, y1) in stripes:
        height = y1 - y0 + 1
        if MIN_STRIPE_HEIGHT <= height <= MAX_STRIPE_HEIGHT and y0 > h * 0.20:
            filtered.append((y0, y1))

    filtered.sort(key=lambda t: t[0])
    return filtered


def _compute_axis_percentages(
    stripe_mask: np.ndarray,
) -> Tuple[float, float, float]:
    """
    Calcule (gauche, centre, droite) en pourcentage pour une bande d'axe donnée,
    à partir d'un masque binaire (h x w) limité à cette bande.

    - On projette horizontalement pour obtenir un masque 1D des colonnes colorées.
    - On repère les segments continus de colonnes colorées.
    - On suppose : segment_gauche, zone centrale (grise), segment_droit.

    Retourne des pourcentages flottants (gauche, centre, droite) qui somment à 100.
    """
    h, w = stripe_mask.shape
    col_color = stripe_mask.any(axis=0)  # True si qq pixel coloré sur la colonne

    # regrouper les colonnes contiguës colorées
    segments: List[Tuple[int, int]] = []
    start = None
    for x, val in enumerate(col_color):
        if val and start is None:
            start = x
        elif not val and start is not None:
            segments.append((start, x - 1))
            start = None
    if start is not None:
        segments.append((start, w - 1))

    # ne garder que les segments significatifs
    big_segments = [(s, e) for (s, e) in segments if (e - s + 1) >= MIN_SEGMENT_WIDTH]

    if not big_segments:
        # aucune info exploitable
        return 0.0, 100.0, 0.0

    if len(big_segments) == 1:
        # un seul grand segment coloré => très majoritaire d'un côté
        s, e = big_segments[0]
        length = e - s + 1
        # on considère que la barre couvre pratiquement 100 %
        return 0.0, 0.0, 100.0

    # au moins deux segments : gauche et droite de l'axe
    left_s, left_e = big_segments[0]
    right_s, right_e = big_segments[-1]

    left_len = left_e - left_s + 1
    right_len = right_e - right_s + 1
    gap_len = max(0, right_s - left_e - 1)

    total = left_len + gap_len + right_len
    if total == 0:
        return 0.0, 0.0, 0.0

    left_pct = left_len / total * 100.0
    centre_pct = gap_len / total * 100.0
    right_pct = right_len / total * 100.0

    # normalisation pour éviter 99.999 ou 100.001
    s = left_pct + centre_pct + right_pct
    left_pct *= 100.0 / s
    centre_pct *= 100.0 / s
    right_pct *= 100.0 / s

    return left_pct, centre_pct, right_pct


def extract_scores_from_image(image_path: str) -> Dict[str, int]:
    """
    Lit une capture d'écran Politiscales et renvoie un dict :
        {
          "constructivisme":  7,
          "essentialisme":  67,
          ...
        }

    Cette version ne dépend pas de Tesseract : elle exploite uniquement
    la géométrie des barres colorées.
    """
    img = Image.open(image_path).convert("RGB")
    w, h = img.size

    # Zone centrale : on évite les marges latérales (icônes, texte, etc.)
    x0 = int(X_START_FRAC * w)
    x1 = int(X_END_FRAC * w)
    if x1 <= x0:
        x0, x1 = 0, w

    sub = img.crop((x0, 0, x1, h))

    # Passage en HSV pour isoler les pixels saturés (= colorés)
    hsv = sub.convert("HSV")
    arr = np.array(hsv)
    S = arr[:, :, 1]
    V = arr[:, :, 2]

    color_mask = (S > SAT_THRESHOLD) & (V > VAL_THRESHOLD)

    # Détection des 8 bandes horizontales correspondant aux axes
    stripes = _find_color_stripes(color_mask)

    scores: Dict[str, int] = {
        name: 0 for pair in AXIS_ORDER for name in pair
    }

    for axis_idx, (left_name, right_name) in enumerate(AXIS_ORDER):
        if axis_idx >= len(stripes):
            # pas de bande détectée pour cet axe
            scores[left_name] = 0
            scores[right_name] = 0
            continue

        y0, y1 = stripes[axis_idx]
        stripe_mask = color_mask[y0:y1 + 1, :]
        left_pct, centre_pct, right_pct = _compute_axis_percentages(stripe_mask)

        # Arrondir en entiers
        l = int(round(left_pct))
        c = int(round(centre_pct))
        r = int(round(right_pct))

        # petite correction : forcer la somme à 100 en ajustant le centre
        total = l + c + r
        if total != 100:
            c = max(0, 100 - l - r)

        scores[left_name] = l
        scores[right_name] = r

    return scores
