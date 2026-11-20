from copy import deepcopy
from urllib.parse import quote, urlencode

import pytest


def test_homepage_redirect(client):
    url = "/"

    response = client.get(url, follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_static_homepage(client):
    url = "/static/index.html"

    response = client.get(url)

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Mergington High School" in response.text
    assert 'id="activities-list"' in response.text


def test_list_activities(client, activity_data):
    expected = deepcopy(activity_data)

    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == expected
    assert activity_data == expected


def test_list_empty_activities(client, activity_data):
    activity_data.clear()

    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == {}


def test_signup_adds_only_selected_participant(client, activity_data):
    email = "new@example.com"
    expected = deepcopy(activity_data)
    expected["Art Club"]["participants"].append(email)

    response = client.post(
        "/activities/Art%20Club/signup", params={"email": email}
    )
    listed = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert activity_data == expected
    assert listed.status_code == 200
    assert listed.json() == expected


@pytest.mark.parametrize(
    ("name", "email", "status", "detail"),
    [
        ("Unknown", "new@example.com", 404, "Activity not found"),
        (
            "Chess Club",
            "michael@example.com",
            400,
            "Student is already registered for this activity",
        ),
    ],
)
def test_signup_rejected_without_state_change(
    client, activity_data, name, email, status, detail
):
    before = deepcopy(activity_data)
    url = f"/activities/{quote(name, safe='')}/signup"

    response = client.post(url, params={"email": email})

    assert response.status_code == status
    assert response.json() == {"detail": detail}
    assert activity_data == before


@pytest.mark.parametrize("operation", ["signup", "unregister"])
def test_missing_email(client, activity_data, operation):
    before = deepcopy(activity_data)
    method = "POST" if operation == "signup" else "DELETE"

    response = client.request(method, f"/activities/Chess%20Club/{operation}")

    assert response.status_code == 422
    assert any(
        error["loc"] == ["query", "email"]
        for error in response.json()["detail"]
    )
    assert activity_data == before


def test_unregister_removes_only_selected_participant(client, activity_data):
    email = "michael@example.com"
    expected = deepcopy(activity_data)
    expected["Chess Club"]["participants"].remove(email)

    response = client.delete(
        "/activities/Chess%20Club/unregister", params={"email": email}
    )
    listed = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert activity_data == expected
    assert listed.status_code == 200
    assert listed.json() == expected


@pytest.mark.parametrize(
    ("name", "detail"),
    [
        ("Unknown", "Activity not found"),
        ("Chess Club", "Student is not registered for this activity"),
    ],
)
def test_unregister_rejected_without_state_change(client, activity_data, name, detail):
    before = deepcopy(activity_data)
    url = f"/activities/{quote(name, safe='')}/unregister"

    response = client.delete(url, params={"email": "missing@example.com"})

    assert response.status_code == 404
    assert response.json() == {"detail": detail}
    assert activity_data == before


def test_repeated_unregister(client, activity_data):
    url = "/activities/Chess%20Club/unregister"
    params = {"email": "michael@example.com"}
    initial_removal = client.delete(url, params=params)
    assert initial_removal.status_code == 200
    before = deepcopy(activity_data)

    response = client.delete(url, params=params)

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not registered for this activity"}
    assert activity_data == before


def test_signup_unregister_and_reregister(client, activity_data):
    url = "/activities/Art%20Club"
    email = "student+art@example.com"
    params = {"email": email}
    expected_participants = [email]

    signup = client.post(f"{url}/signup", params=params)
    unregister = client.delete(f"{url}/unregister", params=params)
    reregister = client.post(f"{url}/signup", params=params)

    assert signup.status_code == 200
    assert unregister.status_code == 200
    assert reregister.status_code == 200
    assert activity_data["Art Club"]["participants"] == expected_participants


@pytest.mark.parametrize("operation", ["signup", "unregister"])
def test_encoded_activity_and_email(client, activity_data, operation):
    name = "Arts & Crafts"
    email = "student+arts@example.com"
    if operation == "signup":
        activity_data[name]["participants"].clear()
    url = (
        f"/activities/{quote(name, safe='')}/{operation}"
        f"?{urlencode({'email': email})}"
    )
    method = "POST" if operation == "signup" else "DELETE"
    expected_participants = [email] if operation == "signup" else []

    response = client.request(method, url)

    assert response.status_code == 200
    assert activity_data[name]["participants"] == expected_participants
