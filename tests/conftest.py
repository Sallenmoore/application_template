import os
import sys

import mongomock
import pytest
from autonomous.db import connect, disconnect
from mongomock.gridfs import enable_gridfs_integration

from app import create_app
from models.user import User
from models.world import World

# # Add the 'app' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
enable_gridfs_integration()


@pytest.fixture(scope="module", autouse=True)
def test_db():
    disconnect()
    connect(
        "test_image_db",
        host="mongodb://localhost",
        mongo_client_class=mongomock.MongoClient,
    )
    yield
    disconnect()
