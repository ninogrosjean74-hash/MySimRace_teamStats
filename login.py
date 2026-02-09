import requests


def create_session() -> requests.Session:
    return requests.Session()


def login_MSR(session: requests.Session, userName: str, password: str):

    mysimrace_login_url = "https://mysimrace.com/api/login.php"

    payload = {
        "pilot_name": userName,
        "password": password,
    }
    response = session.post(mysimrace_login_url, data=payload)

    if response.status_code != 200:
        return False

    if session.cookies.get("__Host-PHPSESSID") is None:
        return False

    return True


def logout_MSR(session: requests.Session) -> None:
    session.cookies.clear()


#### A VIRER C EST JUSTE POUR DES TESTS #####
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
        return

    data = resp.json()["pilots"]

    return data


if __name__ == "__main__":
    username = None
    password = None
    session = create_session()
    print(session.cookies.get("__Host-PHPSESSID"))
    # print(session.cookies)
    login_MSR(session, username, password)
    data = fetch_team_stats_track_car(97, "GT3", session)
    print(session.cookies.get("__Host-PHPSESSID"))
    logout_MSR(session)
    data0 = fetch_team_stats_track_car(97, "LMP2", session)
