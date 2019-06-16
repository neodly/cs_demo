from cs_demo.schema import BoardSchema


def test_board_schema_validation():
    validated_board = BoardSchema().load({"name": "a" * 21})
    assert validated_board.errors
    assert "Longer than maximum length 20." == validated_board.errors["name"][0]
