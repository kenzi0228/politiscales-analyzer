import streamlit as st
from ocr.politiscales_ocr import extract_scores_from_image
from model.transforms import apply_transformations_and_get_coordinates
from plotting.plot_2d import plot_positions
from data.personalities import PERSONALITIES

st.set_page_config(
    page_title="Politiscales – Positionnement politique",
    layout="wide"
)

st.title("Positionnement politique (2D)")
st.caption("Économique : Gauche ↔ Droite | Sociétal : Libertaire ↔ Autoritaire")

uploaded = st.file_uploader(
    "Importer une capture Politiscales",
    type=["png", "jpg", "jpeg"]
)

user_point = None

if uploaded:
    scores = extract_scores_from_image(uploaded)
    x, y = apply_transformations_and_get_coordinates(scores)
    user_point = {"name": "Vous", "x": x, "y": y}

filter_group = st.selectbox(
    "Filtre personnalités",
    ["Toutes"] + sorted(set(p["group"] for p in PERSONALITIES))
)

filtered = [
    p for p in PERSONALITIES
    if filter_group == "Toutes" or p["group"] == filter_group
]

fig = plot_positions(user_point, filtered)
st.pyplot(fig)
