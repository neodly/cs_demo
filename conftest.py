from cs_demo import create_app, config
import mongoengine as me
import pytest


@pytest.fixture
def app():
    app = create_app(config.TestingConfig)
    return app


@pytest.fixture(scope="function")
def mongo(request):
    db = me.connect("testdb", alias="TESTDB", host="mongomock://localhost")
    yield db
    db.get_database("test").drop_collection("board")
    db.drop_database("testdb")
    db.close()
