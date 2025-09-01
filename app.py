import streamlit as st
import numpy as np
import random
import string
from pathlib import Path
from html import escape
import streamlit.components.v1 as components

st.set_page_config(page_title="Le Néologène", page_icon="🔤", layout="centered")

ALPH = string.ascii_lowercase
I2A = {i: c for i, c in enumerate(ALPH)}
V = len(ALPH)

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

# ---- UI minimal & esthétique
st.markdown("""
<style>
h1 { text-align:center; font-weight:800; letter-spacing:.02em; }
.main-card {
  max-width: 680px; margin: 1.5rem auto 0 auto;
  background: linear-gradient(180deg, #ffffff, #fafbff);
  border: 1px solid rgba(0,0,0,.06);
  border-radius: 18px; padding: 1.25rem 1.25rem 1rem 1.25rem;
  box-shadow: 0 6px 24px rgba(0,0,0,.06);
}
.controls {
  display:flex; gap:.75rem; align-items:center; justify-content:center; flex-wrap:wrap;
}
.word-wrap {
  position: relative; text-align:center; padding: 1rem 2.25rem 0 2.25rem;
}
.word {
  font-size: clamp(36px, 7vw, 56px);
  font-weight: 800; letter-spacing: .06em; line-height: 1.05;
}
.copy-btn {
  position: absolute; right: .5rem; top: .25rem;
  border: 1px solid rgba(0,0,0,.08);
  background: #ffffff; border-radius: 10px;
  padding: .35rem .55rem; cursor: pointer; font-size: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,.05);
  opacity: .65; transition: all .2s ease;
}
.copy-btn:hover { opacity: 1; transform: translateY(-1px); }
.hint {
  text-align:center; color: #6b7280; font-size: .9rem; margin-top: .5rem;
}
footer {visibility: hidden;} /* cache la barre footer streamlit */
</style>
""", unsafe_allow_html=True)

st.title("Le Néologène")

if "last_word" not in st.session_state:
    st.session_state.last_word = ""

# Contrôles
L = st.slider("Longueur du mot", min_value=4, max_value=8, value=7, step=1)

col1, = st.columns(1)
with col1:
    st.button("🎲 Nouveau mot", use_container_width=True,
              on_click=lambda: st.session_state.update(
                  last_word=generate_word(L, Start_top, H_top, End_top))
              )

# Carte mot + bouton copier discret
word = st.session_state.last_word or "—"
safe_word = escape(word)

html_card = f"""
<div class="main-card">
  <div class="word-wrap">
    <button class="copy-btn" title="Copier"
      onclick="navigator.clipboard.writeText('{safe_word}');
               this.innerText='✔'; setTimeout(()=>this.innerText='📋', 1200);">📋</button>
    <div class="word">{safe_word}</div>
  </div>
  <div class="hint">Clique sur 🎲 pour proposer un nouveau mot • Bouton 📋 pour copier</div>
</div>
"""
components.html(html_card, height=220, scrolling=False)
