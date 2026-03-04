from fastapi import status


def test_root_redirect(client):
    # disable following redirects to inspect the initial response
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (
        status.HTTP_307_TEMPORARY_REDIRECT,
        status.HTTP_308_PERMANENT_REDIRECT,
    )
    assert response.headers["location"].endswith("/static/index.html")


def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # expect the dictionary to have several known activities
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_successful_signup(client):
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # ensure not already there
    before = client.get("/activities").json()[activity]["participants"]
    assert email not in before

    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert response.status_code == status.HTTP_200_OK
    assert "Signed up" in response.json().get("message", "")

    after = client.get("/activities").json()[activity]["participants"]
    assert email in after


def test_duplicate_signup(client):
    activity = "Programming Class"
    existing = client.get("/activities").json()[activity]["participants"][0]
    response = client.post(f"/activities/{activity}/signup", params={"email": existing})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json().get("detail", "")


def test_signup_nonexistent_activity(client):
    response = client.post("/activities/NotAnActivity/signup", params={"email": "foo@bar.com"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_successful_removal(client):
    activity = "Gym Class"
    email = client.get("/activities").json()[activity]["participants"][0]
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert response.status_code == status.HTTP_200_OK
    assert "Removed" in response.json().get("message", "")

    after = client.get("/activities").json()[activity]["participants"]
    assert email not in after


def test_remove_not_registered(client):
    activity = "Tennis Club"
    response = client.delete(f"/activities/{activity}/participants", params={"email": "nobody@here.com"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not registered" in response.json().get("detail", "")


def test_remove_nonexistent_activity(client):
    response = client.delete("/activities/Nope/participants", params={"email": "x@y.com"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
