from __future__ import annotations

import math
from typing import Dict, Tuple

# Les 16 variables attendues (0..100)
VARS = [
    "constructivisme", "essentialisme",
    "justice_rehabilitative", "justice_punitive",
    "progressisme", "conservatisme",
    "internationalisme", "nationalisme",
    "communisme", "capitalisme",
    "regulation", "laissez_faire",
    "ecologie", "productivisme",
    "revolution", "reformisme",
]


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _norm(score_0_100: float) -> float:
    return _clip01(score_0_100 / 100.0)


# 4 méthodes imposées (et utilisées)
def T_log(v: float) -> float:
    # ln(1 + v) avec v dans [0,1] => [0, ln(2)]
    return math.log(1.0 + _clip01(v))

def T_sigmoid(v: float) -> float:
    # 1 / (1 + e^{-v}) ; v dans [0,1] => proche [0.5, 0.731]
    return 1.0 / (1.0 + math.exp(-_clip01(v)))

def T_ratio(v_i: float, v_j: float) -> float:
    # v_i / (1 + v_j) ; v_i,v_j in [0,1]
    return _clip01(v_i) / (1.0 + _clip01(v_j))

def I_abs(v_i: float, v_j: float) -> float:
    # |v_i - v_j|
    return abs(_clip01(v_i) - _clip01(v_j))


def apply_transformations_and_get_coordinates(scores: Dict[str, int]) -> Tuple[float, float]:
    """
    Sortie (x, y) dans environ [-4, 4] (clippé) :
      x = économie (gauche<0, droite>0)
      y = sociétal (libertaire<0, autoritaire>0)

    On combine :
      - Logarithme (décroissance influence extrêmes)
      - Sigmoïde (lissage)
      - Ratio pondéré (empêche dominance)
      - Distance absolue (écart entre opposés)
    """

    # Normalisation
    v = {k: _norm(scores.get(k, 0)) for k in VARS}

    # --- Économie : (capitalisme vs communisme), (laissez-faire vs régulation),
    #                (productivisme vs écologie), (réformisme vs révolution)
    cap = v["capitalisme"]
    com = v["communisme"]
    lf  = v["laissez_faire"]
    reg = v["regulation"]
    prod= v["productivisme"]
    eco = v["ecologie"]
    ref = v["reformisme"]
    rev = v["revolution"]

    # Transformations de base
    cap_t = 0.55*T_log(cap) + 0.45*T_sigmoid(cap)
    com_t = 0.55*T_log(com) + 0.45*T_sigmoid(com)

    lf_t  = 0.55*T_log(lf)  + 0.45*T_sigmoid(lf)
    reg_t = 0.55*T_log(reg) + 0.45*T_sigmoid(reg)

    prod_t= 0.55*T_log(prod)+ 0.45*T_sigmoid(prod)
    eco_t = 0.55*T_log(eco) + 0.45*T_sigmoid(eco)

    ref_t = 0.55*T_log(ref) + 0.45*T_sigmoid(ref)
    rev_t = 0.55*T_log(rev) + 0.45*T_sigmoid(rev)

    # Ratios (pondération croisée pour limiter dominance)
    cap_r = T_ratio(cap, com)
    com_r = T_ratio(com, cap)
    lf_r  = T_ratio(lf, reg)
    reg_r = T_ratio(reg, lf)
    prod_r= T_ratio(prod, eco)
    eco_r = T_ratio(eco, prod)
    ref_r = T_ratio(ref, rev)
    rev_r = T_ratio(rev, ref)

    # Distances (écart gauche/droite)
    d_cc   = I_abs(com, cap)
    d_lfr  = I_abs(reg, lf)
    d_pe   = I_abs(eco, prod)
    d_rr   = I_abs(rev, ref)

    # Score éco brut
    # Droite: cap, lf, prod, ref ; Gauche: com, reg, eco, rev
    x_raw = (
        1.30*(cap_t - com_t) +
        1.10*(lf_t  - reg_t) +
        0.90*(prod_t- eco_t) +
        0.70*(ref_t - rev_t) +
        0.60*(cap_r - com_r) +
        0.50*(lf_r  - reg_r) +
        0.30*(prod_r- eco_r) +
        0.30*(ref_r - rev_r) +
        0.50*(d_cc + d_lfr + d_pe + d_rr) * (0.5)  # augmente “conviction”
    )

    # --- Sociétal : constructivisme vs essentialisme, réhabilitative vs punitive,
    #               progressisme vs conservatisme, internationalisme vs nationalisme
    cons = v["constructivisme"]
    ess  = v["essentialisme"]
    rehab= v["justice_rehabilitative"]
    puni = v["justice_punitive"]
    prog = v["progressisme"]
    conv = v["conservatisme"]
    intl = v["internationalisme"]
    nat  = v["nationalisme"]

    # Transformations
    # Libertaire/progressiste : constructivisme, rehab, prog, intl
    # Autoritaire/traditionnel : essentialisme, puni, conv, nat
    cons_t = 0.55*T_log(cons)  + 0.45*T_sigmoid(cons)
    ess_t  = 0.55*T_log(ess)   + 0.45*T_sigmoid(ess)
    rehab_t= 0.55*T_log(rehab) + 0.45*T_sigmoid(rehab)
    puni_t = 0.55*T_log(puni)  + 0.45*T_sigmoid(puni)
    prog_t = 0.55*T_log(prog)  + 0.45*T_sigmoid(prog)
    conv_t = 0.55*T_log(conv)  + 0.45*T_sigmoid(conv)
    intl_t = 0.55*T_log(intl)  + 0.45*T_sigmoid(intl)
    nat_t  = 0.55*T_log(nat)   + 0.45*T_sigmoid(nat)

    # Ratios
    cons_r = T_ratio(cons, ess)
    ess_r  = T_ratio(ess, cons)
    rehab_r= T_ratio(rehab, puni)
    puni_r = T_ratio(puni, rehab)
    prog_r = T_ratio(prog, conv)
    conv_r = T_ratio(conv, prog)
    intl_r = T_ratio(intl, nat)
    nat_r  = T_ratio(nat, intl)

    # Distances
    d_ce = I_abs(cons, ess)
    d_j  = I_abs(rehab, puni)
    d_pc = I_abs(prog, conv)
    d_in = I_abs(intl, nat)

    # y_raw : Autoritaire (positif) - Libertaire (négatif)
    y_raw = (
        1.15*(ess_t  - cons_t) +
        1.10*(puni_t - rehab_t) +
        1.05*(conv_t - prog_t) +
        0.85*(nat_t  - intl_t) +
        0.55*(ess_r  - cons_r) +
        0.50*(puni_r - rehab_r) +
        0.45*(conv_r - prog_r) +
        0.35*(nat_r  - intl_r) +
        0.45*(d_ce + d_j + d_pc + d_in) * (0.5)
    )

    # Mise à l’échelle vers ~[-4,4] et clip
    # (coeff empirique : stable visuellement)
    x = max(-4.0, min(4.0, 7.0 * (x_raw - 0.0)))
    y = max(-4.0, min(4.0, 7.0 * (y_raw - 0.0)))

    return x, y
