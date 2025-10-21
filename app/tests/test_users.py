
# test if conftest inserted 20 users in the memory
def test_users_seeded_corectly(gen_dummy_users):
    total = len(gen_dummy_users)
    usernames = [user.username for user in gen_dummy_users]
    assert 'hr.mohammadi' in usernames
    assert total == 20


def test_invalid_response_404(client):
    payload = {
        "username": "test",
        "password": "test"
    }

    response = client.post("/users/login", json=payload)
    assert response.status_code == 404

    payload_incorrect_username = {
        "username": "testusername",
        "password": "12345678"
    }

    response = client.post("/users/login", json=payload_incorrect_username)
    assert response.status_code == 404


def test_invalid_response_401(client):
    payload_incorrect_password = {
        "username": "hr.mohammadi",
        "password": "test"
    }

    response = client.post("/users/login", json=payload_incorrect_password)
    assert response.status_code == 401


def test_valid_login_response_200(client):

    payload_incorrect_password = {
        "username": "hr.mohammadi",
        "password": "12345678"
    }

    response = client.post("/users/login", json=payload_incorrect_password)
    assert response.status_code == 200


def test_register_response_201(client):
    payload = {
        "username": "m.mohammadi",
        "password": "12345678",
        "is_active": "False",
        "user_type": "admin"
    }

    response = client.post("/users/register", json=payload)
    assert response.status_code == 201
