import streamlit as st
import numpy as np
import random
import string
from pathlib import Path

st.set_page_config(page_title="Générateur de mots", page_icon="🔤", layout="centered")

ALPH = string.ascii_lowercase
I2A = {i: c for i, c in enumerate(ALPH)}
V = len(ALPH)

@st.cache_resource
def load_matrices():
    paths = {"start": Path("start.npy"), "h": Path("h.npy"), "end": Path("end.npy")}
    for name, p in paths.items():
        if not p.exists():
            st.error(f"Fichier manquant : {p.name}. Assure-toi de l'avoir enregistré.")
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

st.title("🔤 Générateur de mots (bigrammes)")
st.caption("Charge les matrices .npy (start.npy, h.npy, end.npy) et génère des mots ressemblant au français.")

if "last_word" not in st.session_state:
    st.session_state.last_word = ""

L = st.slider("Longueur du mot", min_value=3, max_value=10, value=7, step=1)
col1, col2 = st.columns([1,1])

with col1:
    if st.button("🎲 Nouveau mot"):
        st.session_state.last_word = generate_word(L, Start_top, H_top, End_top)

with col2:
    if st.button("🔁 Recharger matrices"):
        load_matrices.clear()
        Start_top, H_top, End_top = load_matrices()
        st.success("Matrices rechargées.")

st.header("Résultat")
big = f"<div style='font-size: 3rem; font-weight: 700; letter-spacing: .05em;'>{st.session_state.last_word or '—'}</div>"
st.markdown(big, unsafe_allow_html=True)

with st.expander("Infos matrices"):
    st.write(f"Start: {Start_top.shape}")
    st.write(f"H: {H_top.shape}")
    st.write(f"End: {End_top.shape}")
