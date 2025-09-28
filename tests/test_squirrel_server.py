import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
from squirrel_server import SquirrelServerHandler

class FakeRequest(SquirrelServerHandler):
    def __init__(self, method="GET", path="/squirrels", body=None):
        self.path = path
        self.headers = {"Content-Length": str(len(body) if body else 0)}
        self.rfile = FakeRFile(body)
        self.wfile = FakeWFile()
        self.responses = []
        self.sent_headers = []
        self.sent_body = None

    def send_response(self, code):
        self.responses.append(code)

    def send_header(self, key, value):
        self.sent_headers.append((key, value))

    def end_headers(self):
        pass

    def handle404(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"404 Not Found")

class FakeRFile:
    def __init__(self, body):
        self.body = body.encode("utf-8") if body else b""

    def read(self, length):
        return self.body

class FakeWFile:
    def __init__(self):
        self.data = b""

    def write(self, b):
        self.data += b

def describe_squirrel_server():

    def test_handleSquirrelsIndex(mocker):
        fake = FakeRequest()
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrels.return_value = [{"id": 1, "name": "Fluffy", "size": "large"}]

        fake.handleSquirrelsIndex()

        assert 200 in fake.responses
        assert ("Content-Type", "application/json") in fake.sent_headers
        assert b"Fluffy" in fake.wfile.data
        mock_db.return_value.getSquirrels.assert_called_once()

    def test_handleSquirrelsRetrieve_found(mocker):
        fake = FakeRequest(path="/squirrels/1")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = {"id": 1, "name": "Fluffy", "size": "large"}

        fake.handleSquirrelsRetrieve("1")

        assert 200 in fake.responses
        assert b"Fluffy" in fake.wfile.data
        mock_db.return_value.getSquirrel.assert_called_once_with("1")

    def test_handleSquirrelsRetrieve_not_found(mocker):
        fake = FakeRequest(path="/squirrels/99")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = None

        fake.handleSquirrelsRetrieve("99")

        assert 404 in fake.responses
        mock_db.return_value.getSquirrel.assert_called_once_with("99")

    def test_handleSquirrelsCreate(mocker):
        body = "name=Fluffy&size=large"
        fake = FakeRequest(method="POST", path="/squirrels", body=body)
        mock_db = mocker.patch("squirrel_server.SquirrelDB")

        fake.handleSquirrelsCreate()

        assert 201 in fake.responses
        mock_db.return_value.createSquirrel.assert_called_once_with("Fluffy", "large")

    def test_handleSquirrelsUpdate_found(mocker):
        body = "name=Fluffy&size=small"
        fake = FakeRequest(method="PUT", path="/squirrels/1", body=body)
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = {"id": 1}

        fake.handleSquirrelsUpdate("1")

        assert 204 in fake.responses
        mock_db.return_value.updateSquirrel.assert_called_once_with("1", "Fluffy", "small")

    def test_handleSquirrelsUpdate_not_found(mocker):
        fake = FakeRequest(method="PUT", path="/squirrels/99", body="name=Ghost&size=tiny")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = None

        fake.handleSquirrelsUpdate("99")

        assert 404 in fake.responses
        mock_db.return_value.getSquirrel.assert_called_once_with("99")

    def test_handleSquirrelsDelete_found(mocker):
        fake = FakeRequest(path="/squirrels/1")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = {"id": 1}

        fake.handleSquirrelsDelete("1")

        assert 204 in fake.responses
        mock_db.return_value.deleteSquirrel.assert_called_once_with("1")

    def test_handleSquirrelsDelete_not_found(mocker):
        fake = FakeRequest(path="/squirrels/99")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = None

        fake.handleSquirrelsDelete("99")

        assert 404 in fake.responses
        mock_db.return_value.getSquirrel.assert_called_once_with("99")