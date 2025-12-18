# ui.py
from __future__ import annotations

import random
import tkinter as tk
from typing import Dict, List

from tkinter import filedialog, messagebox
from tkinter import ttk

from ocr import extract_scores_from_image
from model import apply_transformations_and_get_coordinates

from personalities_data import PersonalityPoint, get_personalities

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Rectangle, Ellipse

plt.style.use("ggplot")


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# ============================================================
#  APPLICATION PRINCIPALE
# ============================================================

class WizardApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Politiscales Avancé - Graphe 2D (16 variables)")
        self.geometry("1000x700")
        self.minsize(860, 620)
        self.configure(bg="#f5f5f5")

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background="#f5f5f5")
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), background="#f5f5f5")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 11), background="#f5f5f5")
        style.configure("TLabel", font=("Segoe UI", 10), background="#f5f5f5")
        style.configure("TButton", font=("Segoe UI", 10), padding=6)
        style.configure("TEntry", font=("Segoe UI", 10))

        self.num_people = 0
        self.current_index = 0
        self.people_data: List[dict] = []

        # Base personnalités depuis module dédié
        self.personalities: List[PersonalityPoint] = get_personalities()

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=15, pady=15)

        self.frame_start = StartFrame(self.container, self)
        self.frame_form = FormFrame(self.container, self)
        self.frame_plot = PlotFrame(self.container, self)

        self.show_frame(self.frame_start)

    def show_frame(self, frame: ttk.Frame):
        for f in (self.frame_start, self.frame_form, self.frame_plot):
            f.pack_forget()
        frame.pack(fill="both", expand=True)

    def go_to_form(self, nb: int):
        self.num_people = nb
        self.current_index = 0
        self.people_data.clear()
        self.frame_form.reset_form()
        self.show_frame(self.frame_form)

    def save_person_data(self, name: str, scores: Dict[str, int]):
        x_val, y_val = apply_transformations_and_get_coordinates(scores)
        x_val = _clamp(float(x_val), -4.0, 4.0)
        y_val = _clamp(float(y_val), -4.0, 4.0)
        self.people_data.append({"name": name, "scores": scores, "x": x_val, "y": y_val})

    def next_person(self):
        self.current_index += 1
        if self.current_index < self.num_people:
            self.frame_form.reset_form()
        else:
            self.frame_plot.create_plot(self.people_data)
            self.show_frame(self.frame_plot)


# ============================================================
#  PAGE 1 — Nombre de personnes
# ============================================================

class StartFrame(ttk.Frame):
    def __init__(self, parent, app: WizardApp):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Politiscales – Assistant de positionnement politique", style="Title.TLabel").pack(pady=(10, 5))
        ttk.Label(
            self,
            text="Indiquez le nombre de personnes à comparer.\nVous renseignerez ensuite leurs 16 scores.",
            style="Subtitle.TLabel",
            wraplength=700,
            justify="center",
        ).pack(pady=(0, 20))

        form = ttk.Frame(self)
        form.pack()

        ttk.Label(form, text="Nombre de personnes :", anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry = ttk.Entry(form, width=10)
        self.entry.grid(row=0, column=1, pady=5, sticky="w")

        self.btn = ttk.Button(self, text="Commencer", command=self.on_next)
        self.btn.pack(pady=20)

        # Entrée => Commencer
        self.entry.bind("<Return>", lambda e: self.on_next())

    def on_next(self):
        try:
            n = int(self.entry.get())
            if n <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Erreur", "Veuillez saisir un entier strictement positif.")
            return
        self.app.go_to_form(n)


# ============================================================
#  PAGE 2 — Saisie + OCR
# ============================================================

class FormFrame(ttk.Frame):
    def __init__(self, parent, app: WizardApp):
        super().__init__(parent)
        self.app = app

        header = ttk.Frame(self)
        header.pack(fill="x")

        self.title_label = ttk.Label(header, text="Saisie des informations", style="Title.TLabel")
        self.title_label.pack(anchor="w")

        ttk.Label(
            header,
            text="Pour chaque personne, indiquez le prénom et les 16 scores (0 à 100).",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        scroll_container = ttk.Frame(self)
        scroll_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(scroll_container, bg="#f5f5f5", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.inner_frame = ttk.Frame(self.canvas)
        self.inner_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.inner_window, width=e.width))

        name_block = ttk.Frame(self.inner_frame)
        name_block.pack(fill="x", pady=(0, 10))

        ttk.Label(name_block, text="Prénom :", width=18).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        self.name_entry = ttk.Entry(name_block, width=25)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=5)

        self.btn_ocr = ttk.Button(name_block, text="Importer depuis une capture Politiscales (OCR)", command=self.import_from_screenshot)
        self.btn_ocr.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="w")

        self.var_list = [
            "constructivisme", "essentialisme",
            "justice_rehabilitative", "justice_punitive",
            "progressisme", "conservatisme",
            "internationalisme", "nationalisme",
            "communisme", "capitalisme",
            "regulation", "laissez_faire",
            "ecologie", "productivisme",
            "revolution", "reformisme",
        ]

        self.entries: Dict[str, ttk.Entry] = {}
        fields = ttk.Frame(self.inner_frame)
        fields.pack(fill="x")

        for i, var in enumerate(self.var_list):
            fr = ttk.Frame(fields)
            fr.grid(row=i // 2, column=i % 2, padx=10, pady=6, sticky="w")
            ttk.Label(fr, text=f"{var.replace('_', ' ').capitalize()} (0–100) :").pack(anchor="w")
            e = ttk.Entry(fr, width=10)
            e.pack(anchor="w")
            self.entries[var] = e
            e.bind("<Return>", lambda ev: self.validate_form())

        self.btn_validate = ttk.Button(self, text="Valider & personne suivante", command=self.validate_form)
        self.btn_validate.pack(pady=12)

        self.name_entry.bind("<Return>", lambda e: self.validate_form())
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def reset_form(self):
        idx = self.app.current_index + 1
        total = self.app.num_people
        self.title_label.config(text=f"Saisie pour la personne {idx}/{total}")

        self.name_entry.delete(0, tk.END)
        for e in self.entries.values():
            e.delete(0, tk.END)

        self.canvas.yview_moveto(0)
        self.name_entry.focus_set()

    def import_from_screenshot(self):
        path = filedialog.askopenfilename(
            title="Choisir une capture Politiscales",
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp"), ("Tous les fichiers", "*.*")],
        )
        if not path:
            return

        try:
            scores = extract_scores_from_image(path)
        except Exception as e:
            messagebox.showerror("Erreur OCR", str(e))
            return

        found = False
        for key, ent in self.entries.items():
            if key in scores:
                ent.delete(0, tk.END)
                ent.insert(0, str(scores[key]))
                if scores[key] != 0:
                    found = True

        if found:
            messagebox.showinfo("OCR Politiscales", "Scores importés depuis la capture.\nVérifiez puis ajustez si besoin.")
        else:
            messagebox.showwarning("OCR Politiscales", "Aucun score n'a été détecté automatiquement.")

    def validate_form(self):
        name = self.name_entry.get().strip()
        if not name:
            name = f"Personne_{self.app.current_index + 1}"

        scores: Dict[str, int] = {}
        try:
            for key, ent in self.entries.items():
                v = ent.get().strip() or "0"
                v_int = int(v)
                if not (0 <= v_int <= 100):
                    raise ValueError
                scores[key] = v_int
        except Exception:
            messagebox.showerror("Erreur", "Tous les scores doivent être des entiers entre 0 et 100.")
            return

        self.app.save_person_data(name, scores)
        self.app.next_person()


# ============================================================
#  PAGE 3 — Graphique + Filtre Personnalités
# ============================================================

class PlotFrame(ttk.Frame):
    def __init__(self, parent, app: WizardApp):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Positionnement politique (2D)", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="Axe économique : Gauche ↔ Droite | Axe sociétal : Libertaire ↔ Autoritaire",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(0, 6))

        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", pady=(0, 8))

        ttk.Label(ctrl, text="Filtre personnalités :", anchor="w").pack(side="left", padx=(0, 8))

        self.filter_var = tk.StringVar(value="Aucun")

        categories = sorted({p.category for p in self.app.personalities})
        self.filter_combo = ttk.Combobox(
            ctrl,
            textvariable=self.filter_var,
            state="readonly",
            width=22,
            values=["Aucun", "Tous"] + categories,
        )
        self.filter_combo.pack(side="left")
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        self.btn_apply = ttk.Button(ctrl, text="Appliquer", command=self.apply_filter)
        self.btn_apply.pack(side="left", padx=8)

        ttk.Label(ctrl, text="(Entrée = appliquer)").pack(side="left", padx=(8, 0))

        graph = ttk.Frame(self)
        graph.pack(fill="both", expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7.6, 6.8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar = ttk.Frame(graph)
        toolbar.pack(fill="x")
        NavigationToolbar2Tk(self.canvas, toolbar)

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", pady=(8, 0))
        self.btn_save = ttk.Button(bottom, text="Télécharger le graphique (PNG)", command=self.save_figure)
        self.btn_save.pack(side="left")

        self._people_data_cache: List[dict] = []

        # Entrée => appliquer filtre (quand frame visible)
        self.bind_all("<Return>", self._on_enter_plot, add="+")

    def _on_enter_plot(self, event):
        if not self.winfo_ismapped():
            return
        self.apply_filter()

    def create_plot(self, people: List[dict]):
        self._people_data_cache = people[:]
        self._redraw_all()

    def _draw_base(self):
        self.ax.clear()
        self.ax.set_xlim(-4, 4)
        self.ax.set_ylim(-4, 4)

        # Quadrants clairs, lisibles
        self.ax.add_patch(Rectangle((-4, 0), 4, 4, color="#ffcccc", alpha=0.22, zorder=0))   # haut-gauche
        self.ax.add_patch(Rectangle((0, 0), 4, 4, color="#ccffcc", alpha=0.22, zorder=0))    # haut-droit
        self.ax.add_patch(Rectangle((-4, -4), 4, 4, color="#ccccff", alpha=0.22, zorder=0))  # bas-gauche
        self.ax.add_patch(Rectangle((0, -4), 4, 4, color="#ffffcc", alpha=0.22, zorder=0))   # bas-droit

        self.ax.axhline(0, color="black", linewidth=1.2, zorder=3)
        self.ax.axvline(0, color="black", linewidth=1.2, zorder=3)
        self.ax.grid(True, linestyle="--", alpha=0.35, zorder=1)

        self.ax.set_xlabel("Économique : Gauche (x < 0)  |  Droite (x > 0)", fontsize=9)
        self.ax.set_ylabel("Sociétal   : Libertaire (y < 0)  |  Autoritaire (y > 0)", fontsize=9)

    def _draw_people(self):
        for p in self._people_data_cache:
            color = "#%06x" % random.randint(0, 0xFFFFFF)
            self.ax.plot(p["x"], p["y"], marker="x", color=color, markersize=8, linewidth=2, zorder=6)
            self.ax.text(p["x"], p["y"], " " + p["name"], color=color, fontsize=9, zorder=7)

    def _draw_personalities_overlay(self):
        selection = (self.filter_var.get() or "Aucun").strip()

        if selection == "Aucun":
            return

        if selection == "Tous":
            pts = self.app.personalities
        else:
            pts = [p for p in self.app.personalities if p.category.lower() == selection.lower()]

        # Ellipses grises légères : tu peux customiser ensuite (couleur par catégorie)
        for p in pts:
            ux = _clamp(float(p.ux), 0.15, 1.2)
            uy = _clamp(float(p.uy), 0.15, 1.2)

            ell = Ellipse(
                (p.x, p.y),
                width=2 * ux,
                height=2 * uy,
                alpha=0.18,
                linewidth=1.1,
                edgecolor="black",
                facecolor="gray",
                zorder=2,
            )
            self.ax.add_patch(ell)
            self.ax.text(
                p.x,
                p.y,
                p.name,
                fontsize=8,
                ha="center",
                va="center",
                color="black",
                alpha=0.85,
                zorder=4,
            )

    def _redraw_all(self):
        self._draw_base()
        self._draw_personalities_overlay()
        self._draw_people()
        self.fig.tight_layout()
        self.canvas.draw()

    def apply_filter(self):
        self._redraw_all()

    def save_figure(self):
        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if f:
            self.fig.savefig(f, dpi=300)
            messagebox.showinfo("Image", f"Graphique sauvegardé dans : {f}")
