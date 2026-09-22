from urllib.parse import quote


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_details_and_participants(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    activities = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity in activities
    assert activities[expected_activity]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert "michael@mergington.edu" in activities[expected_activity]["participants"]


def test_signup_adds_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_for_unknown_activity_returns_not_found(client):
    # Arrange
    activity = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_duplicate_signup_returns_bad_request(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activities[activity]["participants"].count(email) == 1


def test_signup_without_email_returns_validation_error(client):
    # Arrange
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup")

    # Assert
    assert response.status_code == 422


def test_unregister_removes_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{quote(activity)}/participants/{quote(email)}")
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity}"}
    assert email not in activities[activity]["participants"]


def test_unregister_from_unknown_activity_returns_not_found(client):
    # Arrange
    activity = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{quote(activity)}/participants/{quote(email)}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_unknown_participant_returns_not_found(client):
    # Arrange
    activity = "Chess Club"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/{quote(activity)}/participants/{quote(email)}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}


def test_repeated_unregister_returns_not_found(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    path = f"/activities/{quote(activity)}/participants/{quote(email)}"

    # Act
    first_response = client.delete(path)
    second_response = client.delete(path)

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 404
    assert second_response.json() == {"detail": "Participant not found"}