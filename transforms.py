# transforms.py
import math

def log_transform(v, alpha=1.0):
    """
    Logarithme : T(v) = ln(1 + alpha * v), v ∈ [0,1]
    """
    if v <= 0:
        return 0.0
    return math.log(1 + alpha * v)

def power_transform(v, beta=1.2):
    """
    Puissance : T(v) = v^beta, v ∈ [0,1]
    """
    return v ** beta

def sigmoid_transform(v, a=1.0, b=0.5):
    """
    Sigmoïde : T(v) = 1 / (1 + e^(-a * (v - b))), v ∈ [0,1]
    """
    return 1.0 / (1.0 + math.exp(-a * (v - b)))

def ratio_transform(v1, v2, k=1.0):
    """
    Ratio pondéré : T(v1, v2) = v1 / (1 + k * v2)
    Evite qu'une seule variable domine.
    """
    return v1 / (1.0 + k * v2)

def absolute_distance(a, b):
    """
    Distance absolue : |a - b|
    """
    return abs(a - b)
