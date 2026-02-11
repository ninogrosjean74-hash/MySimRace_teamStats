import pandas as pd
import numpy as np


def format_time_MinS_2_S(aStr: str) -> float | None:
    """
    Docstring for format_time_MinS_2_S

    :param aStr: time with format 'mm:ss.xxx'
    :type aStr: str
    :return: time in s
    :rtype: float | None
    """

    if not type(aStr) == str:
        return None

    m, s = aStr.split(":")
    m = int(m)
    s = float(s)
    return float(60 * m + s)


def get_ohneSpeed_times(df) -> pd.DataFrame:
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
    return RPdf


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


def comp_performance(pilot_data, temps_ref) -> dict:
    if pilot_data["best_time"] is None or pd.isna(temps_ref):
        pilot_data["performance"] = None
    else:
        perf = pilot_data["best_time_ms"] / 1000 / temps_ref * 100 - 100
        pilot_data["performance"] = perf
    return pilot_data


def comp_all_performances(all_data_raw: dict, ohne_speed_MSR: pd.DataFrame) -> None:
    """
    Compute performance for the whole dataset
    Computed in place None returned

    :param all_data_raw: dataset fetched from MSR
    :type all_data_raw: dict
    :param ohne_speed_MSR: ohne_speed dataframe with MSR format
    :type ohne_speed_MSR: pd.DataFrame
    :return: None
    """
    data: dict = all_data_raw["data"]
    for (track_id, car), track_car_data in data.items():
        ohne_speed_lap_time_s = ohne_speed_MSR.loc[track_id].loc[car]

        for pilot_data in track_car_data.values():
            comp_performance(pilot_data, ohne_speed_lap_time_s)


def init_average_performances_pilots(all_data) -> dict:
    data = all_data["data"]

    track_car_data = list(data.values())[0]
    pilots_average_performance = {}
    for pilot_data in track_car_data.values():
        pilots_average_performance[pilot_data["id"]] = {
            "id": pilot_data["id"],
            "name": pilot_data["name"],
            "all_performances": [],
            "average_performance": None,
            "deviation": None,
            "rank": None,
        }

    return pilots_average_performance


def comp_average_perf(all_data: dict, cars: list[str], nb_Laps_mini=10) -> dict:
    """
    Docstring for comp_average_perf

    :param cars: list of car to average
    :type cars: list[str]
    :param nb_Laps_mini: nb laps mini to count a perf
    :return: dict in the format of init_average_perfomances_pilots
    :rtype: dict
    """
    pilots_average_performance = init_average_performances_pilots(all_data)

    data = all_data["data"]
    for (track_id, car), track_car_data in data.items():
        if not car in cars:
            continue

        # gather all performances
        for pilot_data in track_car_data.values():
            if pilot_data["laps"] >= nb_Laps_mini:
                pilots_average_performance[pilot_data["id"]]["all_performances"].append(pilot_data["performance"])

    # compute average performance
    for pilot_data in pilots_average_performance.values():
        if len(pilot_data["all_performances"]) > 0:
            pilot_data["average_performance"] = np.mean(pilot_data["all_performances"])
            pilot_data["deviation"] = np.std(pilot_data["all_performances"])

    # compute rank
    pilots_list = pilots_average_performance.values()
    pilots_with_perf = [pilot for pilot in pilots_list if pilot["average_performance"] is not None]
    pilots_sorted = sorted(pilots_with_perf, key=lambda pilot: pilot["average_performance"])
    for r, pilot in enumerate(pilots_sorted, start=1):
        pilot["rank"] = r

    return pilots_average_performance


def get_showable_leaderboard_df(all_data, cars, nb_Laps_mini=10) -> pd.DataFrame:
    list = [pilot for pilot in comp_average_perf(all_data, cars, nb_Laps_mini).values() if pilot["rank"] is not None]
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


def get_personnal_track_car_data(all_data: dict, pilot_id: int) -> list[dict]:
    pilot_list = []
    tracks = all_data["tracks"]
    data = all_data["data"]
    for (track_id, car), track_car_data in data.items():
        pilot_data = track_car_data[pilot_id]
        pilot_list.append(
            {
                "track_id": track_id,
                "track": tracks[track_id]["track_name"],
                "car": car,
                "best_lap": pilot_data["best_time"],
                "performance": pilot_data["performance"],
                "laps": pilot_data["laps"],
            }
        )
    return pilot_list


def init_pilot_table(all_data: dict) -> dict:
    tracks = all_data["tracks"]
    table = {}
    for t in tracks.values():
        table[t["id"]] = {"Track": t["track_name"]}

    return table


def get_showable_pilot_df(all_data: dict, pilot_id: int, data="Performance") -> pd.DataFrame:
    pilot_list = get_personnal_track_car_data(all_data, pilot_id)
    pilot_table = init_pilot_table(all_data)
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
