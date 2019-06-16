from uuid import uuid4

from flask import Blueprint, abort, jsonify, request
from marshmallow.exceptions import ValidationError

from ..models import Board
from ..schema import BoardSchema, DataSetSchema, TestRunSchema

api = Blueprint("api", __name__)


@api.route("/boards", methods=["POST"])
def create_board():
    schema = BoardSchema(strict=True)
    data = request.get_json() or {}
    try:
        validated_board = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    board = validated_board.data.save()
    return jsonify(schema.dump(board).data), 201


@api.route("/boards", methods=["GET"])
def get_boards():
    schema = BoardSchema(many=True)
    return jsonify({"boards": schema.dump(Board.objects.all()).data})


@api.route("/boards/<board_name>", methods=["GET"])
def get_board(board_name):
    schema = BoardSchema()
    return jsonify(schema.dump(Board.objects.get_or_404(name=board_name)).data)


@api.route("/boards/<board_name>/tests", methods=["POST"])
def create_test_run(board_name):
    board_schema = BoardSchema()
    test_run_schema = TestRunSchema()
    try:
        board_schema.load({"name": board_name})
    except ValidationError as err:
        return jsonify(err.messages), 400
    board = Board.objects.get_or_404(name=board_name)
    test_id = uuid4()
    test_run = test_run_schema.load({"test_id": test_id}).data
    board.test_runs.append(test_run)
    board.save()

    return jsonify(test_run_schema.dump(test_run).data), 201


@api.route("/boards/<board_name>/tests", methods=["GET"])
def get_test_runs(board_name):
    board_schema = BoardSchema()
    test_run_schema = TestRunSchema()
    try:
        board_schema.load({"name": board_name})
    except ValidationError as err:
        return jsonify(err.messages), 400
    board = Board.objects.get_or_404(name=board_name)

    return jsonify({"test_runs": test_run_schema.dump(board.test_runs, many=True).data}), 200


@api.route("/boards/<board_name>/tests/<test_id>", methods=["GET"])
def get_test_run(board_name, test_id):
    schema = TestRunSchema()
    board = Board.objects.get_or_404(name=board_name)
    try:
        return jsonify(schema.dump(board.test_runs.get(test_id=test_id)).data), 200
    except Exception:
        abort(404)


@api.route("/boards/<board_name>/tests/<test_id>/datasets", methods=["POST"])
def create_dataset(board_name, test_id):
    data = request.json or {}
    schema = DataSetSchema(strict=True)
    board = Board.objects.get_or_404(name=board_name)
    try:
        test_run = board.test_runs.get(test_id=test_id)
    except Exception:
        abort(404)
    try:
        validated_dataset = schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    dataset = validated_dataset.data
    test_run.datasets.append(dataset)
    board.save()
    return jsonify(schema.dump(dataset).data), 201


@api.route("/boards/<board_name>/tests/<test_id>/datasets/<dataset_name>", methods=["PUT"])
def update_dataset(board_name, test_id, dataset_name):
    schema = DataSetSchema(strict=True)
    board = Board.objects.get_or_404(name=board_name)
    try:
        test_run = board.test_runs.get(test_id=test_id)
    except Exception:
        abort(404)
    try:
        dataset = test_run.datasets.get(name=dataset_name)
    except Exception as err:
        abort(404)
    dataset.data = [*(request.json or [])]
    board.save()
    return jsonify(schema.dump(dataset).data), 200


@api.route("/boards/<board_name>/tests/<test_id>/datasets/<dataset_name>", methods=["GET"])
def get_dataset(board_name, test_id, dataset_name):
    schema = DataSetSchema(strict=True)
    board = Board.objects.get_or_404(name=board_name)
    try:
        test_run = board.test_runs.get(test_id=test_id)
    except Exception:
        abort(404)
    try:
        dataset = test_run.datasets.get(name=dataset_name)
    except Exception as err:
        abort(404)
    board.save()
    return jsonify(schema.dump(dataset).data), 200
