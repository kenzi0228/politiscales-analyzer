from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Union, Optional
import re

import numpy as np
import cv2
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



AXIS_PAIRS: List[Tuple[str, str]] = [
    ("constructivisme", "essentialisme"),
    ("justice_rehabilitative", "justice_punitive"),
    ("progressisme", "conservatisme"),
    ("internationalisme", "nationalisme"),
    ("communisme", "capitalisme"),
    ("regulation", "laissez_faire"),
    ("ecologie", "productivisme"),
    ("revolution", "reformisme"),
]


def _empty_scores() -> Dict[str, int]:
    d: Dict[str, int] = {}
    for a, b in AXIS_PAIRS:
        d[a] = 0
        d[b] = 0
    return d


@dataclass
class Token:
    x: float
    y: float
    w: float
    h: float
    conf: float
    value: int


def _preprocess(pil_img: Image.Image) -> np.ndarray:
    # Convert PIL -> OpenCV
    img = np.array(pil_img.convert("RGB"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Upscale si petit
    h, w = img.shape[:2]
    if w < 1200:
        scale = 1200 / float(w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

    # Amélioration contraste + binarisation (texte en blanc/noir)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 50, 50)

    # Adaptive threshold aide beaucoup sur screenshots compressés
    thr = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 7
    )

    # Petite ouverture pour enlever bruit
    kernel = np.ones((2, 2), np.uint8)
    thr = cv2.morphologyEx(thr, cv2.MORPH_OPEN, kernel, iterations=1)

    return thr


def extract_scores_from_image(image_input: Union[str, "BytesIO", bytes]) -> Dict[str, int]:
    """
    OCR Politiscales :
    - détecte tokens numériques (0..100) avec positions.
    - regroupe par lignes.
    - pour chaque ligne : récupère un nombre "à gauche" et un "à droite"
      en ignorant le nombre neutre central.
    """

    # Chargement
    if isinstance(image_input, str):
        pil_img = Image.open(image_input)
    else:
        pil_img = Image.open(image_input)

    proc = _preprocess(pil_img)

    # OCR data
    config = "--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789% "
    data = pytesseract.image_to_data(proc, lang="eng+fra", config=config, output_type=pytesseract.Output.DICT)

    tokens: List[Token] = []
    n = len(data["text"])
    for i in range(n):
        text = (data["text"][i] or "").strip()
        if not text:
            continue

        conf = float(data["conf"][i]) if str(data["conf"][i]).replace(".", "", 1).isdigit() else -1.0
        if conf < 10:
            continue

        m = re.search(r"(\d{1,3})\s*%?$", text)
        if not m:
            continue

        val = int(m.group(1))
        if not (0 <= val <= 100):
            continue

        x = float(data["left"][i])
        y = float(data["top"][i])
        w = float(data["width"][i])
        h = float(data["height"][i])

        tokens.append(Token(x=x, y=y, w=w, h=h, conf=conf, value=val))

    if not tokens:
        return _empty_scores()

    # Regroupement par lignes (Y)
    tokens.sort(key=lambda t: (t.y, t.x))
    rows: List[List[Token]] = []
    current: List[Token] = [tokens[0]]
    y_ref = tokens[0].y

    ROW_T = 28.0  # tolérance verticale
    for t in tokens[1:]:
        if abs(t.y - y_ref) <= ROW_T:
            current.append(t)
        else:
            rows.append(current)
            current = [t]
            y_ref = t.y
    rows.append(current)

    # On garde les lignes "utiles" : au moins 2 nombres plausibles
    candidate_rows: List[List[Token]] = []
    for r in rows:
        vals = [t.value for t in r]
        if len(vals) < 2:
            continue
        # évite “149-462” / numéros page en bas : souvent loin en bas + avec '-'
        # notre regex exclut '-' donc ok, mais on filtre aussi valeurs trop répétées
        if max(vals) < 5:  # ligne vide/bruit
            continue
        candidate_rows.append(sorted(r, key=lambda t: t.x))

    if not candidate_rows:
        return _empty_scores()

    # Trier lignes du haut vers bas, garder 8
    candidate_rows.sort(key=lambda r: sum(t.y for t in r) / len(r))
    candidate_rows = candidate_rows[: len(AXIS_PAIRS)]

    # Largeur image (pour séparer gauche/droite)
    img_w = proc.shape[1]
    mid = img_w / 2.0
    margin = img_w * 0.08  # zone centrale à ignorer pour éviter le % "neutre"

    scores = _empty_scores()

    for idx, (left_key, right_key) in enumerate(AXIS_PAIRS):
        if idx >= len(candidate_rows):
            break

        r = candidate_rows[idx]

        left_candidates = [t for t in r if (t.x + t.w/2.0) < (mid - margin)]
        right_candidates = [t for t in r if (t.x + t.w/2.0) > (mid + margin)]

        # fallback si OCR n’a pas bien séparé : on prend extrêmes
        if left_candidates:
            left_val = min(left_candidates, key=lambda t: t.x).value
        else:
            left_val = r[0].value

        if right_candidates:
            right_val = max(right_candidates, key=lambda t: t.x).value
        else:
            right_val = r[-1].value

        scores[left_key] = int(left_val)
        scores[right_key] = int(right_val)

    return scores
