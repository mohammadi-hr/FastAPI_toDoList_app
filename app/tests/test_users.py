

def test_user_login(client):
    payload = {
        "username": "test",
        "password": "test"
    }

    response = client.post("/users/login", json=payload)
    assert response.status_code == 404
