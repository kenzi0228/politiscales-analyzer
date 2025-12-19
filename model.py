# model.py
from transforms import (
    log_transform,
    power_transform,
    sigmoid_transform,
    ratio_transform,
    absolute_distance,
)

def apply_transformations_and_get_coordinates(scores: dict) -> tuple[float, float]:
    """
    Reçoit un dict 'scores' avec 16 clés (0..100) :
      - constructivisme, essentialisme
      - justice_rehabilitative, justice_punitive
      - progressisme, conservatisme
      - internationalisme, nationalisme
      - communisme, capitalisme
      - regulation, laissez_faire
      - ecologie, productivisme
      - revolution, reformisme

    Retourne (x, y) :
      x = axe économique (Gauche / Droite)
      y = axe sociétal   (Libertaire / Autoritaire)
    """

    # 1) Normalisation [0,1]
    cstr = scores['constructivisme']       / 100.0
    ess  = scores['essentialisme']         / 100.0

    jreh = scores['justice_rehabilitative']/ 100.0
    jpun = scores['justice_punitive']      / 100.0

    prog = scores['progressisme']          / 100.0
    cons = scores['conservatisme']         / 100.0

    inter= scores['internationalisme']     / 100.0
    nat  = scores['nationalisme']          / 100.0

    comm = scores['communisme']            / 100.0
    capi = scores['capitalisme']           / 100.0

    reg  = scores['regulation']            / 100.0
    lais = scores['laissez_faire']         / 100.0

    ecol = scores['ecologie']              / 100.0
    prod = scores['productivisme']         / 100.0

    revo = scores['revolution']            / 100.0
    refor= scores['reformisme']            / 100.0

    # 2) Transformations (configurables plus tard)

    # Économique
    comm_t = power_transform(comm, beta=1.3)
    capi_t = log_transform(capi, alpha=1.2)

    reg_t  = sigmoid_transform(reg, a=1.0, b=0.5)
    lais_t = ratio_transform(lais, reg, k=0.8)

    ecol_t = sigmoid_transform(ecol, a=1.2, b=0.4)
    prod_t = power_transform(prod, beta=1.2)

    revo_t  = power_transform(revo, beta=1.3)
    refor_t = ratio_transform(refor, revo, k=0.5)

    # Sociétal
    cstr_t = sigmoid_transform(cstr, a=1.2, b=0.5)
    ess_t  = log_transform(ess, alpha=1.5)

    jreh_t = log_transform(jreh, alpha=1.0)
    jpun_t = power_transform(jpun, beta=1.2)

    prog_t = sigmoid_transform(prog, a=1.0, b=0.5)
    cons_t = power_transform(cons, beta=1.2)

    inter_t = log_transform(inter, alpha=1.3)
    nat_t   = power_transform(nat, beta=1.3)

    # 3) Combinaisons de base

    # Axe économique (x)
    x1 = capi_t - comm_t
    x2 = lais_t - reg_t
    x3 = prod_t - ecol_t
    x4 = refor_t - revo_t
    x_base = x1 + x2 + x3 + x4

    # Axe sociétal (y)
    y1 = cstr_t - ess_t
    y2 = jreh_t - jpun_t
    y3 = prog_t - cons_t
    y4 = inter_t - nat_t
    y_base = y1 + y2 + y3 + y4

    # 4) Interactions par distance absolue
    dist_cc = absolute_distance(comm_t, capi_t)
    dist_pc = absolute_distance(prog_t, cons_t)

    k_dist_cc = 0.3
    k_dist_pc = 0.2

    x = x_base + k_dist_cc * dist_cc
    y = y_base + k_dist_pc * dist_pc

    return x, y
