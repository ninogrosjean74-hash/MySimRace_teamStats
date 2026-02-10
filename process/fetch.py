import requests
import time
import pandas as pd


def fetch_tracks(session: requests.Session) -> dict | None:
    tracks_url = "https://mysimrace.com/api/tracks.php"
    resp = session.get(tracks_url)

    if resp.status_code != 200:
        print(f"erreur lors du chargement des ID circuits")
        return None

    tracks = resp.json()["tracks"]

    tracks_dict = {}
    for track in tracks:
        tracks_dict[track["id"]] = track

    return tracks_dict


def fetch_team_members(session: requests.Session, team_id: int) -> dict:
    team_url = "https://mysimrace.com/api/team_rankings.php"
    param = {"team_id": team_id}
    resp = session.get(team_url, params=param)

    if resp.status_code != 200:
        return None

    members_list = resp.json()["team_stats"]["members"]
    members_dict = {}
    for member in members_list:
        members_dict[member["id"]] = {
            "id": member["id"],
            "name": member["pilot_name"],
            "nationality": member["nationality"],
        }
    return members_dict


def fetch_team_stats(session: requests.Session, track_id: int, car: str) -> dict | None:
    teamProgress_url = "https://mysimrace.com/api/team_progress.php"

    param = {
        "action": "team_stats",
        "track_id": track_id,
        "category": car,
    }
    resp = session.get(teamProgress_url, params=param)
    if resp.status_code != 200:
        print(f"erreur lors du chargement des datas pour :\nTrack id = {track_id}\nCar = {car}")
        return None

    data = resp.json()["pilots"]
    data_dict = {}
    for pilot_data in data:
        data_dict[pilot_data["id"]] = pilot_data

    return data_dict


def fetch_all_data(session: requests.Session) -> dict:
    """
    return all usefull data from MSR

    dict_format = {
        "fetched_time": time.struct_time
        "tracks": {
            track_id: {"track_id":..., "track_name":..., "country_code":...}
            ...
        }

        "pilots": {
            pilot_id: {"id":..., "name":..., "nationality":...}
            ...
        }

        "data": {
            (track_id, car): {
                pilot_id: {data}
                ...
                }
            ...
        }
    }

    """
    tracks = fetch_tracks(session)
    pilots = fetch_team_members(session, 8)  # team id Grid 404 = 8
    all_data = {
        "fetch_time": time.localtime(),
        "tracks": tracks,
        "pilots": pilots,
        "data": {},
    }
    track_ids = tracks.keys()
    cars = ["Hypercar", "LMP2", "LMP2_ELMS", "LMP3", "GT3", "GTE"]

    for id in track_ids:
        for car in cars:
            all_data["data"][(id, car)] = fetch_team_stats(session, id, car)
            # time.sleep(0.2)

    return all_data


def fetch_ohne_speed() -> pd.DataFrame:
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN03UvJDm99byA6vQPZHKOCYVvfxLu1zkJAzdaKyROykzEKY2-Xl1rl1q5znZEf36m88dxMKsY2eaO/pub?output=csv"
    df = pd.read_csv(url)

    return df


if __name__ == "__main__":
    import login

    session = login.create_session()
    login.login_MSR(session, "none", "none")
    all = fetch_all_data(session)
    print(all["data"][(97, "Hypercar")][197])
