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


def is_logged_in(session: requests.Session) -> bool:
    url_test = "https://mysimrace.com/api/tracks.php"
    resp = session.get(url_test)

    return resp.status_code == 200
