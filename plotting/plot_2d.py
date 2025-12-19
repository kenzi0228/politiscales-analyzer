from __future__ import annotations

from typing import Dict, List, Optional
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse


def plot_positions(user_point: Optional[Dict], personalities: List[Dict]):
    fig, ax = plt.subplots(figsize=(11.5, 6.5))

    # limites
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)

    # Quadrants (clairs, lisibles)
    ax.add_patch(Rectangle((-4, 0), 4, 4, color="#fee2e2", alpha=0.45, zorder=0))   # HG
    ax.add_patch(Rectangle((0, 0), 4, 4, color="#dcfce7", alpha=0.45, zorder=0))    # HD
    ax.add_patch(Rectangle((-4, -4), 4, 4, color="#e0e7ff", alpha=0.45, zorder=0))  # BG
    ax.add_patch(Rectangle((0, -4), 4, 4, color="#fef9c3", alpha=0.45, zorder=0))   # BD

    # axes
    ax.axhline(0, color="black", linewidth=1.2)
    ax.axvline(0, color="black", linewidth=1.2)
    ax.grid(True, linestyle="--", alpha=0.35)

    ax.set_xlabel("Économique : Gauche (x < 0)  |  Droite (x > 0)")
    ax.set_ylabel("Sociétal : Libertaire (y < 0)  |  Autoritaire (y > 0)")

    # Personnalités (ellipses)
    for p in personalities:
        x, y = p["x"], p["y"]
        rx = p.get("rx", 0.8)
        ry = p.get("ry", 0.6)
        alpha = p.get("alpha", 0.18)
        edge = p.get("edge", "#111827")
        face = p.get("face", "#94a3b8")

        e = Ellipse((x, y), width=2*rx, height=2*ry, angle=p.get("angle", 0),
                    facecolor=face, edgecolor=edge, linewidth=1.0, alpha=alpha, zorder=2)
        ax.add_patch(e)
        ax.text(x, y, p["name"], ha="center", va="center", fontsize=8, zorder=3, color="#111827")

    # Utilisateur
    if user_point:
        ax.plot(user_point["x"], user_point["y"], marker="x", markersize=9, linewidth=0,
                color="#06b6d4", zorder=5)
        ax.text(user_point["x"], user_point["y"], f" {user_point['name']}",
                fontsize=9, color="#06b6d4", zorder=6)

    fig.tight_layout()
    return fig
