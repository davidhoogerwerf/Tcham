import streamlit as st
import random as rd

st.set_page_config(page_title="Tcham !", page_icon="🎲", layout="centered")

# --- CSS (Animations et style des dés) ---
st.markdown("""
    <style>
        @keyframes roll {
            0% { transform: scale(1) rotate(0deg); }
            50% { transform: scale(1.1) rotate(10deg); }
            100% { transform: scale(1) rotate(0deg); }
        }
        .dice {
            width: 80px; height: 80px;
            background-color: white;
            border-radius: 12px;
            border: 3px solid #333;
            display: grid;
            grid-template: repeat(3, 1fr) / repeat(3, 1fr);
            padding: 8px;
            box-shadow: 4px 4px 0px #bdc3c7;
            margin: auto;
            animation: roll 0.3s ease-in-out;
        }
        .pip { background-color: #e74c3c; border-radius: 50%; width: 14px; height: 14px; align-self: center; justify-self: center; }
        .p1 { grid-area: 2 / 2; } .p2 { grid-area: 1 / 1; } .p3 { grid-area: 1 / 3; }
        .p4 { grid-area: 2 / 1; } .p5 { grid-area: 2 / 3; } .p6 { grid-area: 3 / 1; } .p7 { grid-area: 3 / 3; }
        
        /* Style pour centrer les checkboxes */
        .stCheckbox { text-align: center; display: flex; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

# --- Logique du jeu ---
if "lDes" not in st.session_state:
    st.session_state["lDes"] = [rd.randint(1, 6) for _ in range(3)]

def draw_dice(value):
    pips_map = {1:[1], 2:[2,7], 3:[2,1,7], 4:[2,3,6,7], 5:[2,3,1,6,7], 6:[2,3,4,5,6,7]}
    pips = "".join([f'<div class="pip p{p}"></div>' for p in pips_map[value]])
    return f'<div class="dice">{pips}</div>'

st.title("🎲 Le Tcham !")

# --- Affichage des dés et choix ---
cols = st.columns(3)
garder = [False, False, False]

for i in range(3):
    with cols[i]:
        st.markdown(draw_dice(st.session_state["lDes"][i]), unsafe_allow_html=True)
        # On utilise une clé unique pour chaque checkbox
        garder[i] = st.checkbox(f"Garder", key=f"keep_{i}")

st.markdown("---")

# --- Bouton de lancer ---
if st.button("Lancer les dés...", use_container_width=True):
    for i in range(3):
        if not garder[i]: # Si la case n'est pas cochée, on relance
            st.session_state["lDes"][i] = rd.randint(1, 6)
    st.rerun()

# Aide visuelle
st.info("Cochez les dés que vous voulez conserver !")