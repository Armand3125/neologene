import streamlit as st
import numpy as np
import random
import string
from pathlib import Path

st.set_page_config(page_title="Le Néologène", page_icon="🔤", layout="centered")

ALPH = string.ascii_lowercase
I2A = {i: c for i, c in enumerate(ALPH)}
V = len(ALPH)

URL_DEFINITION = "https://chatgpt.com/g/g-68b5659be5848191b6790872cc11b7fc-le-neologene"

@st.cache_resource
def load_matrices():
    paths = {"start": Path("start.npy"), "h": Path("h.npy"), "end": Path("end.npy")}
    for name, p in paths.items():
        if not p.exists():
            st.error(f"Fichier manquant : {p.name}. Place-le dans le même dossier que l'app.")
            st.stop()
    Start_top = np.load(paths["start"])
    H_top = np.load(paths["h"])
    End_top = np.load(paths["end"])
    return Start_top, H_top, End_top

def sample_from_probs(vec):
    s = vec.sum()
    if s > 0:
        return random.choices(range(V), weights=vec, k=1)[0]
    return random.randrange(V)

def sample_row(P, row_idx):
    row = P[row_idx]
    if row.sum() > 0:
        return random.choices(range(V), weights=row, k=1)[0]
    return random.randrange(V)

def generate_word(L, Start_top, H_top, End_top):
    if L < 2:
        raise ValueError("La longueur doit être ≥ 2")
    first = sample_from_probs(Start_top)
    letters = [first]
    cur = first
    for _ in range(L - 2):
        nxt = sample_row(H_top, cur)
        letters.append(nxt)
        cur = nxt
    last = sample_row(End_top, cur)
    letters.append(last)
    return "".join(I2A[i] for i in letters)

Start_top, H_top, End_top = load_matrices()

st.title("Le Néologène")

if "last_word" not in st.session_state:
    st.session_state.last_word = ""

L = st.slider("Longueur du mot", min_value=4, max_value=8, value=7, step=1)

col1, col2 = st.columns(2)
with col1:
    if st.button("🎲 Nouveau mot", use_container_width=True):
        st.session_state.last_word = generate_word(L, Start_top, H_top, End_top)
with col2:
    # Streamlit >= 1.31 : st.link_button
    try:
        st.link_button("💡 Donner une définition à ce mot", URL_DEFINITION, use_container_width=True)
    except Exception:
        # Fallback si version plus ancienne
        st.markdown(
            f"<a href='{URL_DEFINITION}' target='_blank' style='display:block; text-align:center; padding:.6rem 1rem; border-radius:.5rem; background:#f0f2f6; font-weight:600; text-decoration:none;'>💡 Donner une définition à ce mot</a>",
            unsafe_allow_html=True
        )

big = f"<div style='font-size: 3rem; font-weight: 700; letter-spacing: .05em; text-align:center; margin-top:1rem'>{st.session_state.last_word or '—'}</div>"
st.markdown(big, unsafe_allow_html=True)
