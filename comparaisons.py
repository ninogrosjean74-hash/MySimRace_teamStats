import streamlit as st
import process.treat_data as treat_data
import process.cached_fetch as cfetch


all_data = cfetch.get_all_data()
ohne_speed_MSR_s = cfetch.get_ohne_speed("MSR", "s")
treat_data.comp_all_performances(all_data, ohne_speed_MSR_s)

st.markdown("# Comparaison de pilotes")

#############################################
##### Select box pour choix des pilotes #####
#############################################

team_pilots_dict = all_data["pilots"]
pilots_id_list = list(team_pilots_dict.keys())

selected_pilots = []

n_cols = 5
cols = st.columns(n_cols)
choice = cols[0].selectbox(
    f"Pilote 1",
    pilots_id_list,
    format_func=lambda id: team_pilots_dict[id]["name"],
    key="pilot_1",
    width=300,
)
selected_pilots.append(choice)
i = 1

available = ["None"] + [p for p in pilots_id_list if p not in selected_pilots]
while choice != "None" or len(available) == 0:
    i += 1

    choice = cols[(i - 1) % n_cols].selectbox(
        f"Pilote {i}",
        available,
        format_func=lambda id: team_pilots_dict[id]["name"] if not id == "None" else "None",
        key=f"pilot_{i}",
        width=300,
    )

    if choice != "None":
        selected_pilots.append(choice)

    available = ["None"] + [p for p in pilots_id_list if p not in selected_pilots]


###########################
##### Choix des datas #####
###########################

st.text("\n")
radio = st.radio(
    "Data",
    ["Best time", "Laps"],
    horizontal=True,
)

# On recupere le dataframe
df_full = treat_data.get_showable_comparaison_df(all_data, selected_pilots, data=radio)


#######################################################
##### Application des filtres circuits / voitures #####
#######################################################

st.markdown("### Filtres")
cols = st.columns(2)
tracks_name_list = [track["track_name"] for track in all_data["tracks"].values()]
circuit_filter = cols[0].selectbox(
    "Circuits",
    ["All"] + tracks_name_list,
    width=400,
)

cars_list = ["Hypercar", "LMP2", "LMP2_ELMS", "LMP3", "GT3", "GTE"]
car_filter = cols[1].selectbox(
    "Car",
    ["All"] + cars_list,
    width=400,
)
if circuit_filter == "All" and car_filter == "All":
    df_show = df_full
elif car_filter == "All":
    df_show = df_full.loc[circuit_filter]
elif circuit_filter == "All":
    df_show = df_full.xs(car_filter, level=1)
else:
    df_show = df_full.loc[(circuit_filter, car_filter)].to_frame().transpose()


# Coloring des perfs
# if radio == "Performance":
#     df_show = df_show.style.map(treat_data.perf_coloring)
df_show = df_show.style.map(treat_data.perf_coloring)


# Affichage du tableau
st.table(df_show)
