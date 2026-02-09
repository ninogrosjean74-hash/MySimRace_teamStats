import streamlit as st
import pandas as pd

import connect

radio = st.radio(
    "Category",
    ["Hypercar", "Prototypes", "GT"],
    horizontal=True,
)

if radio == "Hypercar":
    carClass = "Hyp"
elif radio == "Prototypes":
    carClass = "Proto"
elif radio == "GT":
    carClass = "GT"

nb_lap_mini = st.number_input("Minimum number of lap to count the performance", min_value=1, value=10, width=300)

df = connect.get_showable_leaderboard_df(carClass, nb_lap_mini)
st.table(df)

st.markdown("## Note")
st.markdown("Ce classement est calculé à partir d'un indice de performance basé sur les temps de Ohne Speed.")
st.markdown("La performance est calculée pour chaque combo circuit / voiture comme suit :")
st.latex(r"Performance = \frac{meilleur\space temps\space perso}{temps\space Ohne\space Speed} * 100 -100")
st.markdown(
    "La performance moyenne est ensuite calculée en faisant la moyenne des performances sur les différents circuits sur lesquels les pilotes ont roulés."
)
st.markdown(
    "Seuls les circuits ou le pilotes a réalisé au moins le nombre de tour minimu sont pris en compte. Le nombre de valeur sur laquelle la moyenne est calculée est indiqué dans la colonne *Number of values*"
)
st.markdown("La colonne *Standard deviation* indique l'écart type des valeurs.")
st.markdown(
    "Pour que les résultats de ce classement soient le plus représentatif, il est important de noter que le nombre de valeurs doit être le plus grand possible et que l'écart type doit être le plus faible possible."
)
