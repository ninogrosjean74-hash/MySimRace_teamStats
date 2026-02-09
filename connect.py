import requests
import bs4
import getpass
import sys
import json
import time
import os
import glob
import re
from waiting import wait
import streamlit as st
import pandas as pd
import numpy as np


def connect_MSR(userName, password):
    session = requests.Session()

    mysimrace_login_url = "https://mysimrace.com/api/login.php"

    payload = {
        "pilot_name": userName,
        "password": password,
    }
    response = session.post(mysimrace_login_url, data=payload)
    print(response.status_code)
    # apiKey = response.json()["api_key"]

    return session, response


@st.dialog("Connection à MySimRace")
def login_MSR():
    st.session_state["MSR_session"], st.session_state["MSR_connection_resp"] = None, None
    pilot = st.text_input("Nom du pilote")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Submit"):
        st.session_state["MSR_session"], st.session_state["MSR_connection_resp"] = connect_MSR(pilot, password)
        st.rerun()
        return True
    return False


def update_all_MSR_data():
    wait(login_MSR())
    resp = st.session_state["MSR_connection_resp"]
    session = st.session_state["MSR_session"]
    if resp.status_code != 200:
        MSR_connection_failed()
        return
    write_all_combos(session)


@st.dialog("Connection failed")
def MSR_connection_failed():
    st.markdown("Incorrect password or username")
    if st.button("OK"):
        st.rerun()


def fetch_team_stats_track_car(
    track_id: int, car: str, session: requests.Session, write=False, time_ref=None
) -> list[dict] | None:
    teamProgress_url = "https://mysimrace.com/api/team_progress.php"
    param = {
        "action": "team_stats",
        "track_id": track_id,
        "category": car,
    }
    resp = session.get(teamProgress_url, params=param)
    if resp.status_code != 200:
        print(f"erreur lors du chargement des datas pour :\nTrack id = {track_id}\nCar = {car}")
        sys.exit()

    data = resp.json()["pilots"]
    if not time_ref is None:
        for pilot in data:
            comp_perf(pilot, time_ref)
    if write:
        filename = rf"data\{track_id}_{car}.json"
        write_json_list(filename, data)

    return data


def fetch_tracks(session: requests.Session, write=False):
    tracks_url = "https://mysimrace.com/api/tracks.php"
    resp = session.get(tracks_url)
    if resp.status_code != 200:
        print(f"erreur lors du chargement des ID circuits")
        sys.exit()

    tracks = resp.json()["tracks"]
    if write:
        filename = rf"tracks\tracks.json"
        write_json_list(filename, tracks)

    return tracks


def clean_data_tracks():
    [os.unlink(file) for file in glob.glob(r"tracks\*.json")]
    [os.unlink(file) for file in glob.glob(r"data\*.json")]


def write_json_list(filename, L):
    with open(filename, "w") as f:
        f.write("{\n")
        for i, dico in enumerate(L):
            f.write(f'    "{dico["id"]}" : ')
            json.dump(dico, f, ensure_ascii=False)
            if i == len(L) - 1:
                f.write("\n")
            else:
                f.write(",\n")
        f.write("}")


def write_all_combos(session: requests.Session):
    clean_data_tracks()
    cars = ["Hypercar", "LMP2", "LMP2_ELMS", "LMP3", "GT3", "GTE"]
    tracks = fetch_tracks(session, write=True)
    tracks_id = [track["id"] for track in tracks]

    ohne_speed = get_ohneSpeed_times(format="MSR", formatTime="s")[0]

    for trackId in tracks_id:
        for car in cars:
            print(f"Track id : {trackId}\nCar : {car}")
            ohne_speed_lap_time_s = ohne_speed.loc[trackId].loc[car]
            fetch_team_stats_track_car(trackId, car, session, write=True, time_ref=ohne_speed_lap_time_s)
            time.sleep(0.2)
            print("Ok")


@st.cache_data
def export_online_datas() -> pd.DataFrame:
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN03UvJDm99byA6vQPZHKOCYVvfxLu1zkJAzdaKyROykzEKY2-Xl1rl1q5znZEf36m88dxMKsY2eaO/pub?output=csv"
    df = pd.read_csv(url)

    return df


def unformat_time(aStr) -> float | None:
    if not type(aStr) == str:
        return None

    m, s = aStr.split(":")
    m = int(m)
    s = float(s)
    return float(60 * m + s)


def get_ohneSpeed_times(format="OG", formatTime="s"):
    df = export_online_datas()
    circuits = []
    cars = []
    racePace = []
    quali = []
    ci = 0

    for i in range(df.shape[0]):
        line = df.iloc[i]
        # on passe si la ligne ne continent pas d info
        if pd.isna(line.iloc[0]):
            continue

        if line.iloc[0][:13] == "Bahrain (wec)":
            car = line.iloc[0].replace("Bahrain (wec)", "")
        circuit = line.iloc[0].replace(car, "")

        if circuit in circuits:
            ci = circuits.index(circuit)
        else:
            ci = len(circuits)
            circuits.append(circuit)
            racePace.append([])
            quali.append([])

        if not car in cars:
            cars.append(car)
        racePaceTime = line.iloc[4]
        qualiTime = line.iloc[3]
        if pd.isna(racePaceTime):
            racePace[ci].append(0)
        else:
            racePace[ci].append(racePaceTime)

        if pd.isna(qualiTime):
            quali[ci].append(0)
        else:
            quali[ci].append(qualiTime)

    RPdf = pd.DataFrame(racePace, index=circuits, columns=cars)
    Qdf = pd.DataFrame(quali, index=circuits, columns=cars)
    if format == "MSR":
        RPdf = ohne2MSR_notation(RPdf)
        Qdf = ohne2MSR_notation(Qdf)
    elif format == "OG":
        pass
    else:
        raise ValueError("Incorrect format : 'OG' or 'MSR'")
    if formatTime == "s":
        return RPdf.map(unformat_time), Qdf.map(unformat_time)
    elif formatTime == "min.s":
        return RPdf, Qdf
    else:
        raise ValueError("Incorrect formatTime : 's' or 'min.s'")


def ohne2MSR_notation(aDf: pd.DataFrame) -> pd.DataFrame:
    conv_tracks_dict = {
        "Bahrain (wec)": 107,
        "Bahrain (endurance)": 144,
        "Bahrain (outer)": 149,
        "Bahrain (paddock)": 143,
        "Circuit de la Sarthe": 102,
        "Circuit de la Sarthe (straight)": 141,
        "COTA": 111,
        "COTA (national)": 147,
        "Fuji (chicane)": 110,
        "Fuji (classic)": 146,
        "Imola": 109,
        "Interlagos": 97,
        "Monza": 104,
        "Monza (curvagrande)": 145,
        "Portimao": 106,
        "Qatar": 101,
        "Qatar (short)": 139,
        "Silverstone": 100,
        "Sebring": 108,
        "Sebring (school)": 148,
        "Spa": 105,
        "Paul Ricard": 98,
    }
    conv_car_dict = {
        "LMGT3": "GT3",
        "LMH": "Hypercar",
        "LMP3": "LMP3",
        "LMP2elms": "LMP2_ELMS",
        "LMP2wec": "LMP2",
        "GTE": "GTE",
    }
    indexes = aDf.index
    columns = aDf.columns
    new_indexes = []
    new_columns = []
    for index in indexes:
        new_indexes.append(conv_tracks_dict[index])
    for col in columns:
        new_columns.append(conv_car_dict[col])

    aDf.columns = new_columns
    aDf.index = new_indexes
    return aDf


def comp_perf(pilot, temps_ref) -> dict:
    if pilot["best_time"] is None or pd.isna(temps_ref):
        pilot["performance"] = None
    else:
        perf = pilot["best_time_ms"] / 1000 / temps_ref * 100 - 100
        pilot["performance"] = perf
    return pilot


def add_all_performances() -> None:
    ohne_speed = get_ohneSpeed_times(format="MSR")[0]
    files = glob.glob(r"data\*.json")
    for file in files:
        reMatch = re.match(r"^(\d+)_(\w+).json", os.path.basename(file))
        trackId = int(reMatch.group(1))
        car = reMatch.group(2)

        ohne_speed_lap_time_s = ohne_speed.loc[trackId].loc[car]
        with open(file, "r") as f:
            pilots = json.load(f).values()

        for pilot in pilots:
            comp_perf(pilot, ohne_speed_lap_time_s)

        write_json_list(file, pilots)


def init_pilots(filename) -> dict:
    with open(filename, "r") as f:
        pilots = json.load(f).values()
    ret = {}
    for pilot in pilots:
        ret[pilot["id"]] = {
            "id": pilot["id"],
            "name": pilot["name"],
            "all_performances": [],
            "average_performance": None,
            "deviation": None,
            "rank": None,
        }
    return ret


def comp_average_perf(cars: list[str], nb_Laps_mini=10) -> list[dict]:
    all_data = glob.glob(r"data\*.json")
    for i, file in enumerate(all_data):
        if i == 0:
            summary = init_pilots(file)
        reMatch = re.match(r"^(\d+)_(\w+).json", os.path.basename(file))
        car = reMatch.group(2)
        if not car in cars:
            continue

        with open(file, "r") as f:
            pilots = json.load(f).values()

        for pilot in pilots:
            if pilot["laps"] >= nb_Laps_mini:
                summary[pilot["id"]]["all_performances"].append(pilot["performance"])
    for pilot in summary.values():
        if len(pilot["all_performances"]) > 0:
            pilot["average_performance"] = np.mean(pilot["all_performances"])
            pilot["deviation"] = np.std(pilot["all_performances"])
    return summary


def comp_rank(pilots: dict) -> dict:
    pilots_list = pilots.values()
    pilots_with_perf = [pilot for pilot in pilots_list if pilot["average_performance"] is not None]
    pilots_sorted = sorted(pilots_with_perf, key=lambda pilot: pilot["average_performance"])
    for r, pilot in enumerate(pilots_sorted, start=1):
        pilot["rank"] = r

    return pilots


def comp_leaderboard(carClass, nb_Laps_mini=10):
    if carClass == "Hyp":
        cars = ["Hypercar"]
    elif carClass == "Proto":
        cars = ["LMP2", "LMP2_ELMS", "LMP3"]
    elif carClass == "GT":
        cars = ["GT3", "GTE"]
    else:
        print("Incorrect car class")
        return

    summary = comp_average_perf(cars, nb_Laps_mini)
    summary = comp_rank(summary)
    return summary


def get_showable_leaderboard_df(carClass, nb_Laps_mini=10) -> pd.DataFrame:
    list = [pilot for pilot in comp_leaderboard(carClass, nb_Laps_mini).values() if pilot["rank"] is not None]
    nice_list = [
        {
            "Rank": pilot["rank"],
            "Pilot": pilot["name"],
            "Performance": f'{pilot["average_performance"]:.2f}%',
            "Standard deviation": f'{pilot["deviation"]:.2f}',
            "Number of values": f'{len(pilot["all_performances"])}',
        }
        for pilot in list
    ]
    df = pd.DataFrame(nice_list)
    df = df.set_index("Rank")
    df = df.sort_index()
    return df


def get_personnal_infos(pilot_id: int):
    pilot_list = []
    files = glob.glob(r"data\*.json")
    tracks_json = read_json(r"tracks\tracks.json")
    for file in files:
        pilot = read_json(file)[str(pilot_id)]
        reMatch = re.match(r"^(\d+)_(\w+).json", os.path.basename(file))
        trackId = int(reMatch.group(1))
        car = reMatch.group(2)
        pilot_list.append(
            {
                "track_id": trackId,
                "track": tracks_json[str(trackId)]["track_name"],
                "car": car,
                "best_lap": pilot["best_time"],
                "performance": pilot["performance"],
                "laps": pilot["laps"],
            }
        )
    return pilot_list


def init_pilot_table() -> dict:
    tracks = read_json(r"tracks\tracks.json")
    table = {}
    for t in tracks.values():
        table[t["id"]] = {"Track": t["track_name"]}

    return table


def get_team_pilots():
    files = glob.glob(r"data\*.json")
    pilots_dict = {}
    for file in files:
        if re.match(r"^(\d+)_(\w+).json", os.path.basename(file)):
            pilots = read_json(file)
            for pilot in pilots.values():
                pilots_dict[pilot["name"]] = pilot["id"]
            break
    return pilots_dict


def get_showable_pilot_df(pilot_id, data="Performance"):
    pilot_list = get_personnal_infos(pilot_id)
    pilot_table = init_pilot_table()
    for item in pilot_list:
        if data == "Performance":
            if item["best_lap"] is None:
                value = ""
            elif item["performance"] is None:
                value = f'{item["best_lap"]} (no perf)'
            else:
                value = f'{item["best_lap"]} ({item["performance"]:.2f}%)'
        if data == "Laps":
            if item["laps"] != 0:
                value = f'{item["laps"]}'
            else:
                value = ""
        pilot_table[item["track_id"]][item["car"]] = value

    df = pd.DataFrame(pilot_table.values())
    df = df.set_index("Track")
    if data == "Performance":
        df = df.style.map(perf_coloring)
    return df


def read_json(filename) -> dict:
    with open(filename, "r") as f:
        return json.load(f)


def perf_coloring(arg):
    if arg == "":
        return ""
    perf = float(arg.split("(")[1].replace("%)", ""))

    if perf < 1:
        return "background-color: #C9DAF8"
    if perf < 2:
        return "background-color: #D0E0E3"
    if perf < 3:
        return "background-color: #D9EAD3"
    if perf < 4:
        return "background-color: #FFF2CC"
    if perf < 5:
        return "background-color: #FCE5CD"
    if perf < 6:
        return "background-color: #F4CCCC"

    return "background-color: #E6B8AF"


if __name__ == "__main__":
    # conn = connect_MSR()
    # session: requests.Session = conn[0]
    # apiKey: str = conn[1]
    # fetch_tracks(session, True)
    # write_all_combos(session)

    # print()
    # print()
    # combo = fetch_team_stats_track_car(137, "GT3", session)
    # for pilot in combo:
    #     print(pilot)
    # list = get_personnal_infos(197)
    # for item in list:
    #     print(item)

    print(get_showable_pilot_df(197))
    pass
