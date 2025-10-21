# there is a bug in FastAPI-Berear that return 403 instead of 401 error status code
def test_list_all_tasks_401(client):
    response = client.get("/tasks")
    assert response.status_code == 401
