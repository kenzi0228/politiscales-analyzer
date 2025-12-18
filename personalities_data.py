# personalities_data.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class PersonalityPoint:
    name: str
    category: str  # "Philosophe", "Dictateur", "Président", etc.
    x: float
    y: float
    ux: float = 0.45  # demi-largeur ellipse
    uy: float = 0.45  # demi-hauteur ellipse


def get_personalities() -> List[PersonalityPoint]:
    """
    Base de personnalités (positions approximatives 'est.').
    À terme : remplacer par une base sourcée (JSON + références).
    """
    P = PersonalityPoint

    # NB: les coordonnées sont dans le même repère que ton graphe (-4..4).
    return [
        # =========================
        # Philosophes / théoriciens
        # =========================
        P("Karl Marx", "Philosophe", x=-2.8, y=-0.8, ux=0.70, uy=0.55),
        P("Friedrich Hayek", "Philosophe", x=2.2, y=-1.2, ux=0.60, uy=0.55),
        P("Adam Smith (est.)", "Philosophe", x=1.8, y=-0.8, ux=0.55, uy=0.50),
        P("John Locke (est.)", "Philosophe", x=1.2, y=-0.4, ux=0.55, uy=0.50),
        P("Jean-Jacques Rousseau (est.)", "Philosophe", x=-1.2, y=-0.2, ux=0.60, uy=0.55),
        P("Thomas Hobbes", "Philosophe", x=1.0, y=1.7, ux=0.60, uy=0.60),
        P("Machiavel (est.)", "Philosophe", x=1.5, y=2.1, ux=0.60, uy=0.55),
        P("Montesquieu (est.)", "Philosophe", x=0.4, y=-0.1, ux=0.55, uy=0.45),
        P("John Stuart Mill (est.)", "Philosophe", x=0.8, y=-1.0, ux=0.55, uy=0.50),
        P("Hannah Arendt (est.)", "Philosophe", x=0.2, y=0.4, ux=0.55, uy=0.50),
        P("Michel Foucault (est.)", "Philosophe", x=-0.6, y=-1.0, ux=0.60, uy=0.55),
        P("Noam Chomsky (est.)", "Philosophe", x=-1.5, y=-0.8, ux=0.60, uy=0.55),
        P("Ayn Rand (est.)", "Philosophe", x=3.0, y=-0.6, ux=0.60, uy=0.50),

        # =========================
        # Dictateurs / régimes
        # =========================
        P("Joseph Staline", "Dictateur", x=-1.6, y=3.0, ux=0.55, uy=0.55),
        P("Adolf Hitler", "Dictateur", x=3.1, y=3.0, ux=0.55, uy=0.55),
        P("Mao Zedong (est.)", "Dictateur", x=-2.2, y=3.0, ux=0.60, uy=0.55),
        P("Pol Pot (est.)", "Dictateur", x=-2.6, y=3.2, ux=0.60, uy=0.55),
        P("Benito Mussolini (est.)", "Dictateur", x=2.6, y=2.7, ux=0.55, uy=0.55),
        P("Francisco Franco (est.)", "Dictateur", x=2.4, y=2.4, ux=0.55, uy=0.55),
        P("Augusto Pinochet", "Dictateur", x=3.2, y=1.6, ux=0.65, uy=0.55),
        P("Saddam Hussein (est.)", "Dictateur", x=2.2, y=2.6, ux=0.60, uy=0.55),
        P("Kim Jong-un (est.)", "Dictateur", x=-2.8, y=3.4, ux=0.60, uy=0.55),

        # =========================
        # Présidents / dirigeants actuels (est.)
        # =========================
        P("Macron (est.)", "Président", x=1.0, y=0.2, ux=0.55, uy=0.45),
        P("Biden (est.)", "Président", x=0.8, y=0.6, ux=0.55, uy=0.55),
        P("Trump (est.)", "Président", x=2.6, y=2.2, ux=0.65, uy=0.55),
        P("De Gaulle (est.)", "Président", x=1.8, y=1.3, ux=0.60, uy=0.55),
        P("Mitterrand (est.)", "Président", x=-1.0, y=0.5, ux=0.60, uy=0.55),
        P("Thatcher (est.)", "Président", x=2.8, y=1.3, ux=0.60, uy=0.55),
        P("Reagan (est.)", "Président", x=3.0, y=1.2, ux=0.60, uy=0.55),
        P("Churchill (est.)", "Président", x=1.8, y=1.6, ux=0.60, uy=0.55),
        P("Mandela (est.)", "Président", x=-0.4, y=-0.2, ux=0.60, uy=0.55),

        # =========================
        # Catégorie bonus (tu peux l'utiliser)
        # =========================
        P("Robespierre (est.)", "Révolutionnaire", x=-1.8, y=1.8, ux=0.60, uy=0.55),
        P("Lénine (est.)", "Révolutionnaire", x=-2.2, y=2.6, ux=0.60, uy=0.55),
        P("Che Guevara (est.)", "Révolutionnaire", x=-1.8, y=1.6, ux=0.60, uy=0.55),
    ]
