import streamlit as st
import random as rd
import pandas as pd

st.set_page_config(page_title="Tcham !", page_icon="🎲", layout="centered")

# Liste de couleurs distinctes pour les joueurs
COULEURS = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#e67e22", "#1abc9c", "#34495e"]

# --- INITIALISATION ---
if "game_started" not in st.session_state:
    st.session_state.update({
        "game_started": False,
        "historique": {},
        "current_player_idx": 0,
        "nb_lancers": 0,
        "lDes": [6, 6, 6],
        "phase": "jouer",
        "score_tour": 0,
        "players": [],
        "player_colors": {},
        "toggle_anim": True,
        "animation_trigger": [0, 0, 0]
    })

# --- FONCTION DE GÉNÉRATION DES DÉS ---
def draw_dice(value, anim_id, color):
    pips_map = {1:[1], 2:[2,7], 3:[2,1,7], 4:[2,3,6,7], 5:[2,3,1,6,7], 6:[2,3,4,5,6,7]}
    pips_html = "".join([f'<div class="pip p{p}"></div>' for p in pips_map[value]])
    anim_name = f"roll_{anim_id}"
    
    dice_style = f"""
    <style>
        @keyframes {anim_name} {{
            0% {{ transform: rotate(0deg) scale(1); }}
            25% {{ transform: rotate(-15deg) scale(1.1); }}
            70% {{ transform: rotate(15deg) scale(1.1); }}
            100% {{ transform: rotate(0deg) scale(1); }}
        }}
        .dice-{anim_id} {{
            width: 70px; height: 70px;
            background-color: white; border-radius: 12px; 
            border: 4px solid {color};
            display: grid; grid-template: repeat(3, 1fr) / repeat(3, 1fr);
            padding: 8px; box-shadow: 4px 4px 0px #bdc3c7; margin: auto;
            margin-bottom: 20px;
            animation: {anim_name} 0.4s ease-out;
        }}
        .pip {{ background-color: {color}; border-radius: 50%; width: 12px; height: 12px; align-self: center; justify-self: center; }}
        .p1 {{ grid-area: 2 / 2; }} .p2 {{ grid-area: 1 / 1; }} .p3 {{ grid-area: 1 / 3; }}
        .p4 {{ grid-area: 2 / 1; }} .p5 {{ grid-area: 2 / 3; }} .p6 {{ grid-area: 3 / 1; }} .p7 {{ grid-area: 3 / 3; }}
    </style>
    <div class="dice-{anim_id}">{pips_html}</div>
    """
    return dice_style

def get_final_score(des, n):
    d = sorted(des)
    if d == [1, 2, 4]: return {1: 14, 2: 10, 3: 8}[n]
    if d == [1, 1, 1]: return 7
    if d == [6, 6, 6]: return {1: 18, 2: 14, 3: 10}[n]
    if d[0] == 1 and d[1] == 1: return d[2]
    if d[0] == d[1] == d[2]: return d[0] * 2
    if (d[2] - d[1] == 1) and (d[1] - d[0] == 1): return d[2]
    if d == [2, 4, 6]: return 6
    if d == [1, 2, 2]: return 0.5
    return 1.0

# --- ECRAN D'ACCUEIL ---
if not st.session_state.game_started:
    st.title("🎲 Jeux du Tcham") # Changement de texte ici
    nb = st.number_input("Nombre de joueurs", 1, 8, 2)
    names = []
    for i in range(nb):
        names.append(st.text_input(f"Joueur {i+1}", f"Joueur {i+1}"))
    
    if st.button("Démarrer la partie", use_container_width=True):
        st.session_state.players = names
        st.session_state.historique = {n: [] for n in names}
        st.session_state.player_colors = {names[i]: COULEURS[i] for i in range(nb)}
        st.session_state.game_started = True
        st.rerun()

# --- ECRAN DE JEU ---
else:
    player_now = st.session_state.players[st.session_state.current_player_idx]
    current_color = st.session_state.player_colors[player_now]
    
    # Mise en page du titre avec le nom en dessous
    st.markdown(f"<p style='text-align: center; font-size: 20px; margin-bottom: 0px;'>Tour de :</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; color: {current_color}; margin-top: 0px;'>{player_now}</h1>", unsafe_allow_html=True)
    
    # Rappel des scores
    cols_s = st.columns(len(st.session_state.players))
    for i, n in enumerate(st.session_state.players):
        with cols_s[i]:
            c = st.session_state.player_colors[n]
            st.markdown(f"<p style='color:{c}; font-weight:bold; margin-bottom:-5px; text-align:center;'>{n}</p>", unsafe_allow_html=True)
            st.metric("", f"{sum(st.session_state.historique[n])} pts", label_visibility="collapsed")

    st.divider()

    # Affichage des dés
    cols_d = st.columns(3)
    garder = [False, False, False]

    for i in range(3):
        with cols_d[i]:
            st.markdown(draw_dice(st.session_state.lDes[i], st.session_state.animation_trigger[i], current_color), unsafe_allow_html=True)
            if st.session_state.phase == "jouer":
                garder[i] = st.checkbox(
                    "Garder", 
                    key=f"k{i}_p{st.session_state.current_player_idx}_l{st.session_state.nb_lancers}",
                    disabled=(st.session_state.nb_lancers == 0)
                )

    # --- ACTIONS ---
    if st.session_state.phase == "resultat":
        if st.session_state.score_tour >= 7: st.balloons()
        st.success(f"**Score obtenu : {st.session_state.score_tour} points**")
        if st.button(f"Valider le score et passer la main ➡️", use_container_width=True):
            st.session_state.historique[player_now].append(st.session_state.score_tour)
            st.session_state.current_player_idx = (st.session_state.current_player_idx + 1) % len(st.session_state.players)
            st.session_state.nb_lancers = 0
            st.session_state.lDes = [6, 6, 6]
            st.session_state.animation_trigger = [0, 0, 0]
            st.session_state.phase = "jouer"
            st.rerun()
    else:
        if st.session_state.nb_lancers > 0:
            st.write(f"Lancer : **{st.session_state.nb_lancers} / 3**")
        else:
            st.write("")
            
        c1, c2 = st.columns(2)
        bouton_label = "✋ Garder les dés" if all(garder) and st.session_state.nb_lancers > 0 else "🎲 Lancer les dés"
        
        if c1.button(bouton_label, use_container_width=True):
            if st.session_state.nb_lancers > 0 and all(garder):
                st.session_state.score_tour = get_final_score(st.session_state.lDes, st.session_state.nb_lancers)
                st.session_state.phase = "resultat"
                st.rerun()
            
            st.session_state.nb_lancers += 1
            for i in range(3):
                if not garder[i] or st.session_state.nb_lancers == 1:
                    st.session_state.lDes[i] = rd.randint(1, 6)
                    st.session_state.animation_trigger[i] += 1 
            
            d_sorted = sorted(st.session_state.lDes)
            if d_sorted == [1, 2, 2]:
                st.session_state.score_tour = 0.5
                st.session_state.phase = "resultat"
            elif st.session_state.nb_lancers == 3:
                st.session_state.score_tour = get_final_score(st.session_state.lDes, 3)
                st.session_state.phase = "resultat"
            st.rerun()

        if st.session_state.nb_lancers > 0:
            if c2.button("✋ S'arrêter", use_container_width=True):
                st.session_state.score_tour = get_final_score(st.session_state.lDes, st.session_state.nb_lancers)
                st.session_state.phase = "resultat"
                st.rerun()

    # --- HISTORIQUE ---
    st.divider()
    max_tours = max([len(scores) for scores in st.session_state.historique.values()]) or 0
    if max_tours > 0:
        st.subheader("📜 Historique des manches")
        df_data = {n: st.session_state.historique[n] + ["—"] * (max_tours - len(st.session_state.historique[n])) for n in st.session_state.players}
        st.table(pd.DataFrame(df_data, index=[f"Tour {i+1}" for i in range(max_tours)]).astype(str))

    if st.sidebar.button("🔄 Nouvelle Partie"):
        st.session_state.game_started = False
        st.rerun()
