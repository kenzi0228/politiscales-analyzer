from __future__ import annotations

import io
import uuid
import streamlit as st

from ocr import extract_scores_from_image
from model import apply_transformations_and_get_coordinates
from plotting import plot_positions
from data.personalities import PERSONALITIES


# ---------------------------
# Helpers / State
# ---------------------------
AXES = [
    ("Constructivisme", "Essentialisme", "constructivisme", "essentialisme"),
    ("Justice réhabilitative", "Justice punitive", "justice_rehabilitative", "justice_punitive"),
    ("Progressisme", "Conservatisme", "progressisme", "conservatisme"),
    ("Internationalisme", "Nationalisme", "internationalisme", "nationalisme"),
    ("Communisme", "Capitalisme", "communisme", "capitalisme"),
    ("Régulation", "Laissez-faire", "regulation", "laissez_faire"),
    ("Écologie", "Productivisme", "ecologie", "productivisme"),
    ("Révolution", "Réformisme", "revolution", "reformisme"),
]

ALL_VARS = [k for _, _, k, _ in AXES] + [k for _, _, _, k in AXES]


def init_state():
    if "people" not in st.session_state:
        st.session_state.people = []  # list[dict]: {id,name,scores,x,y,color}
    if "selected_person_id" not in st.session_state:
        st.session_state.selected_person_id = None


def empty_scores():
    return {k: 0 for k in ALL_VARS}


def add_person(name: str, scores: dict):
    x, y = apply_transformations_and_get_coordinates(scores)
    pid = str(uuid.uuid4())[:8]
    st.session_state.people.append(
        {"id": pid, "name": name, "scores": scores, "x": float(x), "y": float(y)}
    )
    st.session_state.selected_person_id = pid


def update_person(pid: str, name: str, scores: dict):
    x, y = apply_transformations_and_get_coordinates(scores)
    for p in st.session_state.people:
        if p["id"] == pid:
            p["name"] = name
            p["scores"] = scores
            p["x"] = float(x)
            p["y"] = float(y)
            return


def delete_person(pid: str):
    st.session_state.people = [p for p in st.session_state.people if p["id"] != pid]
    if st.session_state.selected_person_id == pid:
        st.session_state.selected_person_id = st.session_state.people[0]["id"] if st.session_state.people else None


def get_selected():
    pid = st.session_state.selected_person_id
    for p in st.session_state.people:
        if p["id"] == pid:
            return p
    return None


# ---------------------------
# UI Components
# ---------------------------
def axis_pair_slider(left_label, right_label, left_key, right_key, scores: dict, disabled=False):
    """
    Slider unique 0..100 qui impose left+right=100.
    On stocke left = slider, right = 100-slider.
    """
    default_left = int(scores.get(left_key, 50))
    default_left = max(0, min(100, default_left))
    val = st.slider(
        f"{left_label} ↔ {right_label}",
        0, 100,
        default_left,
        disabled=disabled,
        help="Ce slider impose automatiquement une somme à 100 entre les deux pôles."
    )
    scores[left_key] = int(val)
    scores[right_key] = int(100 - val)


def scores_editor(scores: dict, disabled=False):
    """
    Éditeur rapide par axes (8 sliders), somme 100 par axe.
    """
    st.markdown("### Édition des scores (par axes)")
    st.caption("Chaque axe est saisi via un slider unique : la somme des deux pôles est fixée à 100.")
    for (l_lbl, r_lbl, l_key, r_key) in AXES:
        axis_pair_slider(l_lbl, r_lbl, l_key, r_key, scores, disabled=disabled)


def personality_filter_ui():
    st.markdown("### Filtre personnalités")
    enabled = st.checkbox("Afficher les personnalités", value=True)
    if not enabled:
        return []

    groups = ["Toutes"] + sorted({p["group"] for p in PERSONALITIES})
    group = st.selectbox("Catégorie", groups, index=0)
    q = st.text_input("Recherche", placeholder="Nom… (ex: Marx, Hayek, Mandela)")

    filtered = PERSONALITIES
    if group != "Toutes":
        filtered = [p for p in filtered if p["group"] == group]
    if q.strip():
        ql = q.lower().strip()
        filtered = [p for p in filtered if ql in p["name"].lower()]

    st.caption(f"{len(filtered)} personnalité(s) affichée(s).")
    return filtered


# ---------------------------
# Main App
# ---------------------------
st.set_page_config(page_title="Politiscales – Web Analyzer", layout="wide")
init_state()

st.title("Politiscales – Analyzer (Web)")
st.caption("Comparaison multi-personnes + OCR + graphe 2D + filtre personnalités")

tab1, tab2 = st.tabs(["Saisie / Import", "Graphe & Analyse"])

# ============================================================
# TAB 1 — Saisie / Import
# ============================================================
with tab1:
    left, right = st.columns([1.15, 1.85], gap="large")

    with left:
        st.subheader("Ajouter une personne")
        mode = st.radio("Méthode", ["OCR (image Politiscales)", "Saisie manuelle (axes)"], horizontal=False)

        name = st.text_input("Nom / Prénom", value="")

        if mode == "OCR (image Politiscales)":
            up = st.file_uploader("Image Politiscales", type=["png", "jpg", "jpeg"])
            if st.button("Importer via OCR", type="primary", use_container_width=True, disabled=not up):
                scores = empty_scores()
                try:
                    scores = extract_scores_from_image(up)
                    # Si OCR laisse des 0, on garde : l’éditeur permet de corriger
                except Exception as e:
                    st.error(f"OCR impossible : {e}")
                add_person(name.strip() or f"Personne_{len(st.session_state.people)+1}", scores)
                st.success("Personne ajoutée. Passe à l’onglet Graphe pour visualiser.")

        else:
            # Saisie manuelle sur base 50/50 par axe
            tmp_scores = empty_scores()
            for (l_lbl, r_lbl, l_key, r_key) in AXES:
                tmp_scores[l_key] = 50
                tmp_scores[r_key] = 50

            scores_editor(tmp_scores)

            if st.button("Ajouter", type="primary", use_container_width=True):
                add_person(name.strip() or f"Personne_{len(st.session_state.people)+1}", tmp_scores)
                st.success("Personne ajoutée.")

    with right:
        st.subheader("Personnes enregistrées")
        if not st.session_state.people:
            st.info("Aucune personne pour le moment. Ajoute-en une à gauche.")
        else:
            # Liste sélectionnable
            options = {f"{p['name']} (x={p['x']:.2f}, y={p['y']:.2f})": p["id"] for p in st.session_state.people}
            sel_label = st.selectbox("Sélection", list(options.keys()))
            st.session_state.selected_person_id = options[sel_label]

            p = get_selected()
            if p:
                st.markdown("#### Éditer la personne sélectionnée")
                new_name = st.text_input("Nom", value=p["name"], key="edit_name")

                # on copie pour éditer
                edited_scores = dict(p["scores"])
                scores_editor(edited_scores)

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Enregistrer modifications", use_container_width=True):
                        update_person(p["id"], new_name.strip() or p["name"], edited_scores)
                        st.success("Mis à jour.")
                with c2:
                    if st.button("Supprimer", use_container_width=True):
                        delete_person(p["id"])
                        st.warning("Supprimé.")

                st.markdown("#### Scores actuels")
                st.json(get_selected()["scores"])

# ============================================================
# TAB 2 — Graphe & Analyse
# ============================================================
with tab2:
    left, right = st.columns([1.2, 1.8], gap="large")

    with left:
        st.subheader("Options d’affichage")
        show_people = st.checkbox("Afficher mes personnes", value=True)
        show_labels = st.checkbox("Afficher les labels", value=True)
        personalities = personality_filter_ui()

    with right:
        st.subheader("Graphe 2D")
        points = st.session_state.people if show_people else []
        fig = plot_positions(
            user_point=None,  # on ne distingue pas “Vous” ici : on affiche toutes les personnes
            personalities=personalities,
            people_points=points,
            show_labels=show_labels
        )
        st.pyplot(fig, use_container_width=True)

        # Export PNG
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=250)
        st.download_button(
            "Télécharger le graphique (PNG)",
            data=buf.getvalue(),
            file_name="politiscales_plot.png",
            mime="image/png",
            use_container_width=True
        )

        if points:
            st.markdown("### Tableau des personnes")
            st.dataframe(
                [{"Nom": p["name"], "x": round(p["x"], 3), "y": round(p["y"], 3)} for p in points],
                use_container_width=True
            )

        st.caption("Notes : Les personnalités sont des estimations heuristiques. Les sources sont listées dans data/sources.md.")
