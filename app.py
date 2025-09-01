import numpy as np
import random
import string

# ----------------------------
# Paramètres globaux
# ----------------------------
L = 6                  # longueur fixe des mots
k = 6                  # nombre de meilleures transitions à garder
seed = 42
random.seed(seed); np.random.seed(seed)

ALPH = string.ascii_lowercase
A2I = {c:i for i,c in enumerate(ALPH)}
I2A = {i:c for c,i in A2I.items()}
V = len(ALPH)

def clean(word):
    w = word.strip().lower()
    w = "".join(ch for ch in w if ch in ALPH)
    return w

# ----------------------------
# Construction du modèle
# ----------------------------
def build_model(corpus, L=6, k=6):
    words = [clean(x) for x in corpus if x.strip()]
    words = [w for w in words if len(w) >= 2]

    Start = np.zeros(V, dtype=np.int32)
    H = np.zeros((V, V), dtype=np.int32)
    End = np.zeros((V, V), dtype=np.int32)

    for w in words:
        Start[A2I[w[0]]] += 1
        for a, b in zip(w[:-2], w[1:-1]):
            H[A2I[a], A2I[b]] += 1
        End[A2I[w[-2]], A2I[w[-1]]] += 1

    def row_normalize(M):
        M = M.astype(float)
        s = M.sum(axis=1, keepdims=True)
        with np.errstate(divide='ignore', invalid='ignore'):
            P = np.divide(M, s, out=np.zeros_like(M), where=s!=0)
        return P

    H_prob = row_normalize(H)
    End_prob = row_normalize(End)
    Start_prob = Start / Start.sum() if Start.sum() > 0 else np.ones(V) / V

    def topk_mask_rows(P, k):
        P2 = np.zeros_like(P)
        for i in range(P.shape[0]):
            row = P[i]
            if row.sum() == 0:
                continue
            top = np.argsort(row)[-k:]
            P2[i, top] = row[top]
            s = P2[i].sum()
            if s > 0:
                P2[i] /= s
        return P2

    H_top  = topk_mask_rows(H_prob, k)
    End_top = topk_mask_rows(End_prob, k)

    Start_top = np.zeros_like(Start_prob)
    if Start_prob.sum() > 0:
        top = np.argsort(Start_prob)[-k:]
        Start_top[top] = Start_prob[top]
        Start_top /= Start_top.sum()

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

    def generate_word():
        if L < 2:
            raise ValueError("L doit être >= 2")
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

    return Start_top, H_top, End_top, generate_word

# ----------------------------
# Exemple d'utilisation
# ----------------------------
if __name__ == "__main__":
    with open("mots_fr.txt", "r", encoding="utf-8") as f:
        corpus = f.readlines()

    Start_top, H_top, End_top, generate_word = build_model(corpus, L=L, k=k)

    # Génération de mots
    mots = [generate_word() for _ in range(10)]
    print("Mots générés :", mots)

    # Sauvegarde des matrices
    np.save("start.npy", Start_top)
    np.save("h.npy", H_top)
    np.save("end.npy", End_top)
    print("Matrices enregistrées : start.npy, h.npy, end.npy")
