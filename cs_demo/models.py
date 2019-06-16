from flask_mongoengine import Document, MongoEngine
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import (
    DictField,
    EmbeddedDocumentListField,
    ListField,
    StringField,
    UUIDField,
)


class DataSet(EmbeddedDocument):
    name = StringField(required=True)
    data = ListField(DictField(), default=list)

    def __repr__(self):
        return f"<DataSet(name={self.name}>"


class TestRun(EmbeddedDocument):
    test_id = UUIDField(required=True)
    datasets = EmbeddedDocumentListField(DataSet)

    def __repr__(self):
        return f"<TestRun(test_id={self.test_id}>"


class Board(Document):
    name = StringField(max_length=20, required=True)
    test_runs = EmbeddedDocumentListField(TestRun)

    def __repr__(self):
        return f"<Board(name={self.name}>"


db = MongoEngine()
