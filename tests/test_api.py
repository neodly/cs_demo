import json

from flask import url_for

from cs_demo.models import Board

from .factories import BoardFactory, TestRunFactory


def test_creating_board_returns_400_when_no_data(client, mongo):
    res = client.post("/api/boards")

    assert res.status_code == 400


def test_creating_board_returns_is_a_json_api(client, mongo):

    res = client.post("/api/boards")
    assert res.mimetype == "application/json"


def test_creating_board_returns_entry_created_in_database(client, mongo):
    res = client.post(
        "/api/boards",
        data=json.dumps({"name": "TEST BOARD"}),
        headers={"Content-Type": "application/json"},
    )

    assert Board.objects.count() == 1
    assert Board.objects.get(name="TEST BOARD")
    assert "id" in res.json
    assert "name" in res.json


def test_creating_board_return_400_when_validation_data(client, mongo):
    res = client.post(
        "/api/boards",
        data=json.dumps({"name": 200 * "a"}),
        headers={"Content-Type": "application/json"},
    )

    assert res.status_code == 400
    assert Board.objects.count() == 0


def test_getting_boards_list_of_boards(client, mongo):
    BoardFactory()
    res = client.get("/api/boards")

    assert res.status_code == 200
    assert len(res.json["boards"]) == 1
    board = res.json["boards"][0]
    assert "name" in board
    assert "id" in board


def test_gettting_a_board_returns_200(client, mongo):
    board = BoardFactory()
    res = client.get(f"/api/boards/{board.name}")

    assert res.status_code == 200
    assert "name" in board
    assert "id" in board


def test_gettting_a_board_board_not_in_database_404s(client, mongo):
    res = client.get(f"/api/boards/NONEEXISTANTBOARD")

    assert res.status_code == 404


def test_creating_test_run_for_a_board_200(client, mongo):
    board_name = "TEST"
    board = BoardFactory(name=board_name, test_runs=[])
    res = client.post(f"/api/boards/{board_name}/tests")

    assert res.status_code == 201
    board = Board.objects.get(name=board_name)
    assert "test_id" in res.json
    assert len(board.test_runs) == 1
    assert res.json["test_id"] in [str(test_run.test_id) for test_run in board.test_runs]


def test_getting_test_runs_for_a_board_returns_200(client, mongo):
    board_name = "TEST"
    BoardFactory(name=board_name, test_runs=[TestRunFactory()])

    res = client.get(f"/api/boards/{board_name}/tests")

    assert res.status_code == 200
    assert "test_runs" in res.json
    assert len(res.json["test_runs"]) == 1


def test_getting_test_runs_for_a_board_200(client, mongo):
    board_name = "TEST"
    test_run = TestRunFactory()
    BoardFactory(name=board_name, test_runs=[test_run])

    res = client.get(f"/api/boards/{board_name}/tests/{test_run.test_id}")

    assert res.status_code == 200
    assert "test_id" in res.json
    assert res.json["test_id"] == test_run.test_id


def test_getting_a_test_run_for_a_board_200(client, mongo):
    board_name = "TEST"
    test_run = TestRunFactory()
    BoardFactory(name=board_name)

    res = client.get(f"/api/boards/{board_name}/tests/{test_run.test_id}")

    assert res.status_code == 404


def test_creating_dataset_for_a_test_run_201(client, mongo):
    board_name = "TEST"
    TestRunFactory(datasets=[])
    board = BoardFactory(name=board_name, test_runs=[TestRunFactory(datasets=[])])
    res = client.post(
        url_for("api.create_dataset", board_name=board_name, test_id=board.test_runs[0]["test_id"]),
        data=json.dumps({"name": "TEST DATASET", "data": [{"test_data": 1234}]}),
        headers={"Content-Type": "application/json"},
    )

    assert res.status_code == 201
    board = Board.objects.get(name=board_name)
    assert "name" in res.json
    assert "data" in res.json
    assert len(board.test_runs[0].datasets) == 1


def test_updating_dataset_for_a_test_run_200(client, mongo):
    board_name = "TEST"
    board = BoardFactory(name=board_name)
    res = client.put(
        url_for(
            "api.update_dataset",
            board_name=board_name,
            test_id=board.test_runs[0]["test_id"],
            dataset_name=board.test_runs[0].datasets[0].name,
        ),
        data=json.dumps([{"test_data": 1234}]),
        headers={"Content-Type": "application/json"},
    )

    assert res.status_code == 200
    board = Board.objects.get(name=board_name)
    assert "name" in res.json
    assert "data" in res.json
    assert {"test_data": 1234} in res.json["data"]


def test_get_dataset_for_a_test_run_200(client, mongo):
    board_name = "TEST"
    board = BoardFactory(name=board_name)
    board.test_runs[0].datasets[0].data = [{"test_data": 1234}]
    board.save()
    res = client.get(
        url_for(
            "api.get_dataset",
            board_name=board_name,
            test_id=board.test_runs[0]["test_id"],
            dataset_name=board.test_runs[0].datasets[0].name,
        ),
        headers={"Content-Type": "application/json"},
    )
    assert res.status_code == 200
    board = Board.objects.get(name=board_name)
    assert "name" in res.json
    assert "data" in res.json
    assert {"test_data": 1234} in res.json["data"]


def test_get_dataset_invalid_data_set_404s(client, mongo):
    board_name = "TEST"
    board = BoardFactory(name=board_name)
    board.test_runs[0].datasets[0].data = [{"test_data": 1234}]
    board.save()

    res = client.get(
        url_for(
            "api.get_dataset",
            board_name=board_name,
            test_id=board.test_runs[0]["test_id"],
            dataset_name="bad-dataset",
        ),
        headers={"Content-Type": "application/json"},
    )

    assert res.status_code == 404
