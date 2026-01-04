from __future__ import annotations

from typing import Dict, List, Optional
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
import random


def plot_positions(
    user_point: Optional[Dict],
    personalities: List[Dict],
    people_points: Optional[List[Dict]] = None,
    show_labels: bool = True,
):
    fig, ax = plt.subplots(figsize=(11.5, 6.5))

    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)

    # Quadrants clairs
    ax.add_patch(Rectangle((-4, 0), 4, 4, color="#fee2e2", alpha=0.45, zorder=0))   # HG
    ax.add_patch(Rectangle((0, 0), 4, 4, color="#dcfce7", alpha=0.45, zorder=0))    # HD
    ax.add_patch(Rectangle((-4, -4), 4, 4, color="#e0e7ff", alpha=0.45, zorder=0))  # BG
    ax.add_patch(Rectangle((0, -4), 4, 4, color="#fef9c3", alpha=0.45, zorder=0))   # BD

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

        e = Ellipse(
            (x, y),
            width=2 * rx,
            height=2 * ry,
            angle=p.get("angle", 0),
            facecolor=face,
            edgecolor=edge,
            linewidth=1.0,
            alpha=alpha,
            zorder=2,
        )
        ax.add_patch(e)

        if show_labels:
            ax.text(x, y, p["name"], ha="center", va="center", fontsize=8, zorder=3, color="#111827")

    # Points personnes (multi)
    if people_points:
        for p in people_points:
            x, y = p["x"], p["y"]
            name = p["name"]
            color = "#%06x" % random.randint(0, 0xFFFFFF)
            ax.plot(x, y, marker="x", markersize=9, linewidth=0, color=color, zorder=5)
            if show_labels:
                ax.text(x, y, f" {name}", fontsize=9, color=color, zorder=6)

    # (Optionnel) un seul point “user_point” si tu veux réutiliser
    if user_point:
        ax.plot(user_point["x"], user_point["y"], marker="x", markersize=10, linewidth=0,
                color="#06b6d4", zorder=6)
        if show_labels:
            ax.text(user_point["x"], user_point["y"], f" {user_point['name']}",
                    fontsize=10, color="#06b6d4", zorder=7)

    fig.tight_layout()
    return fig
