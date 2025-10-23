import pytest

# there is a bug in FastAPI-Berear that return 403 instead of 401 error status code


def test_list_all_tasks_401(client):
    response = client.get("/tasks")
    assert response.status_code == 401

# config a fakerRdis in order to use redis when runnig this test


# @pytest.mark.asyncio
def test_list_all_tasks_200(authorized_client):
    response = authorized_client.get("/tasks")
    assert response.status_code == 200
