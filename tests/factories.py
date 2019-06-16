from factory import Faker, List, Sequence, SubFactory
from factory.mongoengine import MongoEngineFactory

from cs_demo.models import Board, TestRun, DataSet


class DataSetFactory(MongoEngineFactory):
    name = Sequence(lambda n: f"name {n}")

    class Meta:
        model = DataSet


class TestRunFactory(MongoEngineFactory):
    test_id = Faker("uuid4")
    datasets = List([SubFactory(DataSetFactory)])

    class Meta:
        model = TestRun


class BoardFactory(MongoEngineFactory):
    name = Sequence(lambda n: f"name {n}")
    test_runs = List([SubFactory(TestRunFactory)])

    class Meta:
        model = Board
