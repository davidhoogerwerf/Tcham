import streamlit as st
import random as rd
import pandas as pd

st.set_page_config(page_title="Tcham !", page_icon="🎲", layout="centered")

# --- CSS ---
st.markdown("""
    <style>
        @keyframes roll {
            0% { transform: scale(1) rotate(0deg); }
            50% { transform: scale(1.1) rotate(10deg); }
            100% { transform: scale(1) rotate(0deg); }
        }
        .dice {
            width: 70px; height: 70px;
            background-color: white; border-radius: 12px; border: 3px solid #333;
            display: grid; grid-template: repeat(3, 1fr) / repeat(3, 1fr);
            padding: 8px; box-shadow: 4px 4px 0px #bdc3c7; margin: auto;
            animation: roll 0.3s ease-in-out;
            margin-bottom: 25px; 
        }
        .pip { background-color: #e74c3c; border-radius: 50%; width: 12px; height: 12px; align-self: center; justify-self: center; }
        .p1 { grid-area: 2 / 2; } .p2 { grid-area: 1 / 1; } .p3 { grid-area: 1 / 3; }
        .p4 { grid-area: 2 / 1; } .p5 { grid-area: 2 / 3; } .p6 { grid-area: 3 / 1; } .p7 { grid-area: 3 / 3; }
    </style>
    """, unsafe_allow_html=True)

# --- Initialisation ---
if "game_started" not in st.session_state:
    st.session_state.update({
        "game_started": False,
        "historique": {},
        "current_player_idx": 0,
        "nb_lancers": 0,
        "lDes": [1, 1, 1],
        "phase": "jouer",
        "score_tour": 0
    })

def draw_dice(value):
    pips_map = {1:[1], 2:[2,7], 3:[2,1,7], 4:[2,3,6,7], 5:[2,3,1,6,7], 6:[2,3,4,5,6,7]}
    pips = "".join([f'<div class="pip p{p}"></div>' for p in pips_map[value]])
    return f'<div class="dice">{pips}</div>'

def calculer_score(des, lancer_num):
    d = sorted(des)
    if d == [1, 2, 4]: return {1: 14, 2: 10, 3: 8}[lancer_num]
    if d == [1, 1, 1]: return 7
    if d == [6, 6, 6]: return {1: 18, 2: 14, 3: 10}[lancer_num]
    if d[0] == 1 and d[1] == 1: return d[2]
    if d[0] == d[1] == d[2]: return d[0] * 2
    if (d[2] - d[1] == 1) and (d[1] - d[0] == 1): return d[2]
    if d == [2, 4, 6]: return 6
    if d == [1, 2, 2]: return 0.5
    return 1.0 if lancer_num == 3 else 0

# --- Interface ---
if not st.session_state.game_started:
    st.title("🎲 Configuration du Tcham")
    nb = st.number_input("Nombre de joueurs", 1, 10, 2)
    names = [st.text_input(f"Joueur {i+1}", f"Joueur {i+1}") for i in range(nb)]
    if st.button("Démarrer la partie"):
        st.session_state.players = names
        st.session_state.historique = {n: [] for n in names}
        st.session_state.game_started = True
        st.rerun()
else:
    player_now = st.session_state.players[st.session_state.current_player_idx]
    st.title(f"Tour de : {player_now}")
    
    # Affichage des métriques de score
    cols_s = st.columns(len(st.session_state.players))
    for i, n in enumerate(st.session_state.players):
        cols_s[i].metric(n, f"{sum(st.session_state.historique[n])} pts")

    st.divider()

    # Affichage des dés (toujours visibles)
    cols_d = st.columns(3)
    garder = [False] * 3
    for i in range(3):
        with cols_d[i]:
            st.markdown(draw_dice(st.session_state.lDes[i]), unsafe_allow_html=True)
            # On n'affiche les checkbox que si on est en train de jouer
            if st.session_state.phase == "jouer" and st.session_state.nb_lancers > 0:
                garder[i] = st.checkbox("Garder", key=f"k{i}_{st.session_state.nb_lancers}")

    # --- LOGIQUE D'AFFICHAGE SELON LA PHASE ---
    if st.session_state.phase == "resultat":
        if st.session_state.score_tour >= 7: st.balloons()
        
        st.success(f"**Tour terminé ! Score obtenu : {st.session_state.score_tour} points**")
        
        if st.button("Confirmer et joueur suivant ➡️", use_container_width=True):
            st.session_state.historique[player_now].append(st.session_state.score_tour)
            st.session_state.current_player_idx = (st.session_state.current_player_idx + 1) % len(st.session_state.players)
            st.session_state.nb_lancers = 0
            st.session_state.lDes = [1, 1, 1]
            st.session_state.phase = "jouer"
            st.rerun()
    else:
        st.write(f"Lancer : **{st.session_state.nb_lancers} / 3**")
        c1, c2 = st.columns(2)
        
        if c1.button("🎲 Lancer les dés", use_container_width=True):
            st.session_state.nb_lancers += 1
            for i in range(3):
                if not garder[i] or st.session_state.nb_lancers == 1:
                    st.session_state.lDes[i] = rd.randint(1, 6)
            
            current_des = sorted(st.session_state.lDes)
            if current_des == [1, 2, 2]:
                st.session_state.score_tour = 0.5
                st.session_state.phase = "resultat"
            elif st.session_state.nb_lancers == 3:
                st.session_state.score_tour = calculer_score(st.session_state.lDes, 3)
                st.session_state.phase = "resultat"
            st.rerun()

        if st.session_state.nb_lancers > 0:
            if c2.button("✋ S'arrêter", use_container_width=True):
                st.session_state.score_tour = calculer_score(st.session_state.lDes, st.session_state.nb_lancers)
                st.session_state.phase = "resultat"
                st.rerun()

    # --- TABLEAU DES SCORES ---
    st.divider()
    max_tours = max([len(scores) for scores in st.session_state.historique.values()]) or 0
    if max_tours > 0:
        st.subheader("📜 Historique des manches")
        
        # Création des données
        df_data = {
            n: st.session_state.historique[n] + ["—"] * (max_tours - len(st.session_state.historique[n])) 
            for n in st.session_state.players
        }
        
        # On crée le DataFrame et on force le type en 'object' (ou string) pour éviter l'erreur Arrow
        df = pd.DataFrame(df_data).astype(str) # <--- La correction est ici
        df.index = [f"Tour {i+1}" for i in range(max_tours)]
        
        st.table(df)
