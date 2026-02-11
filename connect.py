import json
import os
import glob
import re
import pandas as pd
import numpy as np


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

    print(comp_leaderboard("Hyp"))
    pass
