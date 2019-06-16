from marshmallow_mongoengine import ModelSchema

from .models import Board, DataSet, TestRun


class BoardSchema(ModelSchema):
    class Meta:
        model = Board


class TestRunSchema(ModelSchema):
    class Meta:
        model = TestRun


class DataSetSchema(ModelSchema):
    class Meta:
        model = DataSet
