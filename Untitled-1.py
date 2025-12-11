import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import math
import random

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle

###############################################################################
# Style Matplotlib (intégré, pas besoin de seaborn)
###############################################################################
plt.style.use("ggplot")

###############################################################################
# Fonctions de transformation
###############################################################################

def log_transform(v, alpha=1.0):
    """
    Logarithme : T(v) = ln(1 + alpha * v)
    v est supposé normalisé dans [0,1].
    """
    if v <= 0:
        return 0.0
    return math.log(1 + alpha * v)

def power_transform(v, beta=1.2):
    """
    Puissance : T(v) = v^beta
    v est supposé normalisé dans [0,1].
    """
    return v ** beta

def sigmoid_transform(v, a=1.0, b=0.5):
    """
    Sigmoïde : T(v) = 1 / (1 + e^(-a * (v - b)))
    v est supposé normalisé dans [0,1].
    """
    return 1.0 / (1.0 + math.exp(-a * (v - b)))

def ratio_transform(v1, v2, k=1.0):
    """
    Ratio pondéré : T(v1, v2) = v1 / (1 + k * v2)
    v1, v2 normalisés dans [0,1].
    Permet d'éviter qu'une seule variable ne domine.
    """
    return v1 / (1.0 + k * v2)

def absolute_distance(a, b):
    """
    Distance absolue : |a - b|
    """
    return abs(a - b)

###############################################################################
# Fonction principale pour calculer (x, y) à partir des 16 variables
###############################################################################

def apply_transformations_and_get_coordinates(scores):
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

    Étapes :
    1) Normalisation [0..1]
    2) Transformations (log, puissance, sigmoïde, ratio)
    3) Combinaisons pour axe économique (x) et axe sociétal (y)
    4) Interactions via distance absolue
    5) Retourne (x, y)
    """


    # 1) Normalisation des 16 variables dans [0,1]
    cstr = scores['constructivisme'] / 100.0
    ess  = scores['essentialisme']   / 100.0

    jreh = scores['justice_rehabilitative'] / 100.0
    jpun = scores['justice_punitive']       / 100.0

    prog = scores['progressisme']    / 100.0
    cons = scores['conservatisme']   / 100.0

    inter= scores['internationalisme']/ 100.0
    nat  = scores['nationalisme']     / 100.0

    comm = scores['communisme']      / 100.0
    capi = scores['capitalisme']     / 100.0

    reg  = scores['regulation']      / 100.0
    lais = scores['laissez_faire']   / 100.0

    ecol = scores['ecologie']        / 100.0
    prod = scores['productivisme']   / 100.0

    revo = scores['revolution']      / 100.0
    refor= scores['reformisme']      / 100.0

    # 2) Transformations non linéaires (choix d'exemple cohérents)

    # Axe ÉCONOMIQUE (x) : Communisme, Capitalisme, Régulation, Laissez-faire,
    # Ecologie, Productivisme, Révolution, Réformisme

    # Communisme => puissance (amplifie les extrêmes égalitaristes)
    comm_t = power_transform(comm, beta=1.3)
    # Capitalisme => log (décroissance de l'effet aux extrêmes)
    capi_t = log_transform(capi, alpha=1.2)

    # Régulation => sigmoïde (effet progressif)
    reg_t  = sigmoid_transform(reg, a=1.0, b=0.5)
    # Laissez-faire => ratio (dépend de la régulation)
    lais_t = ratio_transform(lais, reg, k=0.8)

    # Écologie => sigmoïde (sensibilité progressive)
    ecol_t = sigmoid_transform(ecol, a=1.2, b=0.4)
    # Productivisme => puissance (polarisation forte)
    prod_t = power_transform(prod, beta=1.2)

    # Révolution => puissance (polarisation forte)
    revo_t  = power_transform(revo, beta=1.3)
    # Réformisme => ratio (se “modère” avec le niveau révolutionnaire)
    refor_t = ratio_transform(refor, revo, k=0.5)

    # Axe SOCIÉTAL (y) : Constructivisme, Essentialisme, Justice réhab, Justice punitive,
    # Progressisme, Conservatisme, Internationalisme, Nationalisme

    # Constructivisme => sigmoïde (graduel)
    cstr_t = sigmoid_transform(cstr, a=1.2, b=0.5)
    # Essentialisme => log (fort au début, plafonne)
    ess_t  = log_transform(ess, alpha=1.5)

    # Justice réhabilitative => log
    jreh_t = log_transform(jreh, alpha=1.0)
    # Justice punitive => puissance
    jpun_t = power_transform(jpun, beta=1.2)

    # Progressisme => sigmoïde
    prog_t = sigmoid_transform(prog, a=1.0, b=0.5)
    # Conservatisme => puissance (plus sensible aux hauts niveaux)
    cons_t = power_transform(cons, beta=1.2)

    # Internationalisme => log
    inter_t = log_transform(inter, alpha=1.3)
    # Nationalisme => puissance
    nat_t   = power_transform(nat, beta=1.3)

    # 3) Combinaisons de base pour les axes

    # Axe économique (x) :
    #   x1 = Capitalisme - Communisme
    #   x2 = Laissez-faire - Régulation
    #   x3 = Productivisme - Ecologie
    #   x4 = Réformisme - Révolution
    x1 = capi_t - comm_t
    x2 = lais_t - reg_t
    x3 = prod_t - ecol_t
    x4 = refor_t - revo_t

    x_base = x1 + x2 + x3 + x4

    # Axe sociétal (y) :
    #   y1 = Constructivisme - Essentialisme
    #   y2 = Justice réhabilitative - Justice punitive
    #   y3 = Progressisme - Conservatisme
    #   y4 = Internationalisme - Nationalisme
    y1 = cstr_t - ess_t
    y2 = jreh_t - jpun_t
    y3 = prog_t - cons_t
    y4 = inter_t - nat_t

    y_base = y1 + y2 + y3 + y4

    # 4) Interactions via distance absolue (|V_i - V_j|)

    # Distance Communisme / Capitalisme
    dist_cc = absolute_distance(comm_t, capi_t)
    # Distance Progressisme / Conservatisme
    dist_pc = absolute_distance(prog_t, cons_t)

    # Coefficients d'impact des distances
    k_dist_cc = 0.3
    k_dist_pc = 0.2

    x = x_base + k_dist_cc * dist_cc
    y = y_base + k_dist_pc * dist_pc

    return (x, y)

###############################################################################
# Wizard Tkinter
###############################################################################

class WizardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Politiscales Avancé - Graphe 2D (16 variables)")
        self.geometry("1000x700")

        self.num_people = 0
        self.current_index = 0
        # people_data : liste de dict {name, scores, x, y}
        self.people_data = []

        # Frames
        self.frame_start = StartFrame(self)
        self.frame_form  = FormFrame(self)
        self.frame_plot  = PlotFrame(self)

        self.show_frame(self.frame_start)

    def show_frame(self, frame):
        for f in (self.frame_start, self.frame_form, self.frame_plot):
            f.pack_forget()
        frame.pack(fill="both", expand=True)

    def go_to_form(self, nb):
        self.num_people = nb
        self.current_index = 0
        self.people_data.clear()
        self.frame_form.reset_form()
        self.show_frame(self.frame_form)

    def save_person_data(self, name, scores):
        # Calcul (x,y)
        x_val, y_val = apply_transformations_and_get_coordinates(scores)
        self.people_data.append({
            "name": name,
            "scores": scores,
            "x": x_val,
            "y": y_val
        })

    def next_person(self):
        self.current_index += 1
        if self.current_index < self.num_people:
            self.frame_form.reset_form()
        else:
            self.frame_plot.create_plot(self.people_data)
            self.show_frame(self.frame_plot)

###############################################################################
# StartFrame
###############################################################################

class StartFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        label = tk.Label(self,
                         text="Combien de personnes souhaitez-vous comparer ?",
                         font=("Arial", 16))
        label.pack(pady=20)

        self.entry = tk.Entry(self, font=("Arial", 14))
        self.entry.pack(pady=10)

        btn = tk.Button(self, text="Suivant", font=("Arial", 12),
                        command=self.on_next)
        btn.pack(pady=10)

    def on_next(self):
        try:
            val = int(self.entry.get())
            if val <= 0:
                raise ValueError
            self.master.go_to_form(val)
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez saisir un entier positif.")

###############################################################################
# FormFrame - saisie des 16 variables
###############################################################################

class FormFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.title_label = tk.Label(self, text="Saisie des informations",
                                    font=("Arial", 16))
        self.title_label.pack(pady=10)

        self.name_label = tk.Label(self, text="Prénom :", font=("Arial", 12))
        self.name_label.pack()
        self.name_entry = tk.Entry(self, font=("Arial", 12))
        self.name_entry.pack(pady=5)

        # Liste des 16 variables
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

        self.entries = {}
        for var_name in self.var_list:
            lbl = tk.Label(self,
                           text=f"{var_name.capitalize()} (0..100) :",
                           font=("Arial", 10))
            lbl.pack()
            ent = tk.Entry(self, font=("Arial", 10))
            ent.pack(pady=2)
            self.entries[var_name] = ent

        btn = tk.Button(self, text="Valider & suivant", font=("Arial", 12),
                        command=self.validate_form)
        btn.pack(pady=20)

    def reset_form(self):
        idx = self.master.current_index + 1
        total = self.master.num_people
        self.title_label.config(text=f"Saisie pour la personne {idx}/{total}")

        self.name_entry.delete(0, tk.END)
        for ent in self.entries.values():
            ent.delete(0, tk.END)

    def validate_form(self):
        name = self.name_entry.get().strip()
        if not name:
            name = f"Personne_{self.master.current_index+1}"

        # Lecture des 16 scores
        scores_local = {}
        try:
            for v_name, ent in self.entries.items():
                val_str = ent.get().strip()
                if not val_str:
                    val_str = "0"
                val_int = int(val_str)
                if val_int < 0 or val_int > 100:
                    raise ValueError
                scores_local[v_name] = val_int
        except ValueError:
            messagebox.showerror("Erreur", "Saisissez des entiers entre 0 et 100.")
            return

        self.master.save_person_data(name, scores_local)
        self.master.next_person()

###############################################################################
# PlotFrame - affichage du graphe
###############################################################################

class PlotFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        label = tk.Label(self,
                         text="Positionnement Politique (2D)\nAxe économique vs Axe sociétal",
                         font=("Arial", 14))
        label.pack(pady=10)

        self.figure, self.ax = plt.subplots(figsize=(7,7))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=10, expand=True)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)

        btn_info = tk.Button(btn_frame,
                             text="Informations (formules & scores)",
                             font=("Arial", 10),
                             command=self.show_info)
        btn_info.pack(side=tk.LEFT, padx=5)

        btn_save = tk.Button(btn_frame,
                             text="Télécharger PNG",
                             font=("Arial", 10),
                             command=self.save_figure)
        btn_save.pack(side=tk.LEFT, padx=5)

    def create_plot(self, people_data):
        self.ax.clear()

        # Limites du plan
        self.ax.set_xlim(-4, 4)
        self.ax.set_ylim(-4, 4)

        # Quadrants colorés (fond clair)
        self.ax.add_patch(Rectangle((-4, 0), 4, 4, color="#ffcccc", alpha=0.3))  # haut-gauche
        self.ax.add_patch(Rectangle((0, 0), 4, 4, color="#ccffcc", alpha=0.3))   # haut-droit
        self.ax.add_patch(Rectangle((-4, -4), 4, 4, color="#ccccff", alpha=0.3)) # bas-gauche
        self.ax.add_patch(Rectangle((0, -4), 4, 4, color="#ffffcc", alpha=0.3))  # bas-droit

        # Axes
        self.ax.axhline(0, color="black", linewidth=1)
        self.ax.axvline(0, color="black", linewidth=1)
        self.ax.grid(True, linestyle='--', alpha=0.5)

        self.ax.set_title("Axe Économique (Gauche ↔ Droite) / Axe Sociétal (Libertaire ↔ Autoritaire)",
                          fontsize=11)
        self.ax.set_xlabel("Économique : Gauche (x < 0)  |  Droite (x > 0)")
        self.ax.set_ylabel("Sociétal   : Libertaire (y < 0)  |  Autoritaire (y > 0)")

        # Points
        for person in people_data:
            x = person["x"]
            y = person["y"]
            name = person["name"]
            color = "#%06x" % random.randint(0, 0xFFFFFF)

            self.ax.plot(x, y, marker="x", color=color, markersize=8)
            self.ax.text(x, y, " " + name, fontsize=8, color=color)

        self.canvas.draw()

    def show_info(self):
        win = tk.Toplevel(self)
        win.title("Informations sur le modèle")

        txt = ScrolledText(win, wrap=tk.WORD, width=100, height=30, font=("Courier", 10))
        txt.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        explanation = (
            "===== FORMULES & TRANSFORMATIONS UTILISÉES =====\n\n"
            "Variables (toutes normalisées dans [0,1]) :\n"
            "  Constructivisme, Essentialisme\n"
            "  Justice_rehabilitative, Justice_punitive\n"
            "  Progressisme, Conservatisme\n"
            "  Internationalisme, Nationalisme\n"
            "  Communisme, Capitalisme\n"
            "  Regulation, Laissez_faire\n"
            "  Ecologie, Productivisme\n"
            "  Revolution, Reformisme\n\n"
            "Transformations non linéaires possibles :\n"
            "  - Logarithme  : T(V) = ln(1 + alpha * V)\n"
            "  - Sigmoïde    : T(V) = 1 / (1 + e^(-a*(V - b)))\n"
            "  - Puissance   : T(V) = V^beta\n"
            "  - Ratio pondéré : T(V1, V2) = V1 / (1 + k * V2)\n\n"
            "Axe économique (x) :\n"
            "  x = (T(Capitalisme) - T(Communisme))\n"
            "    + (T(Laissez_faire) - T(Regulation))\n"
            "    + (T(Productivisme) - T(Ecologie))\n"
            "    + (T(Reformisme) - T(Revolution))\n"
            "    + k_dist_cc * |T(Communisme) - T(Capitalisme)|\n\n"
            "Axe sociétal (y) :\n"
            "  y = (T(Constructivisme) - T(Essentialisme))\n"
            "    + (T(Justice_rehabilitative) - T(Justice_punitive))\n"
            "    + (T(Progressisme) - T(Conservatisme))\n"
            "    + (T(Internationalisme) - T(Nationalisme))\n"
            "    + k_dist_pc * |T(Progressisme) - T(Conservatisme)|\n\n"
            "Avec par exemple :\n"
            "  - Communisme : puissance (beta ~ 1.3)\n"
            "  - Capitalisme : logarithme (alpha ~ 1.2)\n"
            "  - Régulation : sigmoïde (a=1, b=0.5)\n"
            "  - Laissez_faire : ratio pondéré avec la régulation\n"
            "  - etc.\n\n"
            "===== COORDONNÉES DES PARTICIPANTS =====\n\n"
        )

        txt.insert(tk.END, explanation)

        for p in self.master.people_data:
            txt.insert(tk.END, f"{p['name']} -> (x={p['x']:.2f}, y={p['y']:.2f})\n")

        txt.configure(state="disabled")

    def save_figure(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("Image PNG", "*.png")])
        if filepath:
            self.figure.savefig(filepath, dpi=300)
            messagebox.showinfo("Enregistrement", f"Image sauvegardée : {filepath}")

###############################################################################
# main
###############################################################################

if __name__ == "__main__":
    app = WizardApp()
    app.mainloop()


