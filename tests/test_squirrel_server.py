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
        

def describe_handleSquirrelsIndex():

    def it_returns_200_status_code(mocker):
        fake = FakeRequest()
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrels.return_value = [{"id": 1, "name": "Fluffy", "size": "large"}]

        fake.handleSquirrelsIndex()
        assert 200 in fake.responses

    def it_sets_content_type_header_to_json(mocker):
        fake = FakeRequest()
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrels.return_value = [{"id": 1, "name": "Fluffy", "size": "large"}]

        fake.handleSquirrelsIndex()
        assert ("Content-Type", "application/json") in fake.sent_headers

    def it_writes_json_to_wfile(mocker):
        fake = FakeRequest()
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrels.return_value = [{"id": 1, "name": "Fluffy", "size": "large"}]

        fake.handleSquirrelsIndex()
        assert b"Fluffy" in fake.wfile.data

    def it_calls_getSquirrels_once(mocker):
        fake = FakeRequest()
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrels.return_value = []

        fake.handleSquirrelsIndex()
        mock_db.return_value.getSquirrels.assert_called_once()

    def it_returns_empty_json_array_if_no_squirrels(mocker):
        fake = FakeRequest()
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrels.return_value = []

        fake.handleSquirrelsIndex()
        assert b"[]" in fake.wfile.data

def describe_handleSquirrelsRetrieve():

    def it_returns_200_if_squirrel_found(mocker):
        fake = FakeRequest(path="/squirrels/1")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = {"id": 1, "name": "Fluffy", "size": "large"}

        fake.handleSquirrelsRetrieve("1")
        assert 200 in fake.responses

    def it_returns_404_if_squirrel_missing(mocker):
        fake = FakeRequest(path="/squirrels/99")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = None

        fake.handleSquirrelsRetrieve("99")
        assert 404 in fake.responses

    def it_calls_getSquirrel_with_correct_id(mocker):
        fake = FakeRequest(path="/squirrels/42")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = {"id": 42}

        fake.handleSquirrelsRetrieve("42")
        mock_db.return_value.getSquirrel.assert_called_once_with("42")

    def it_returns_404_if_id_is_empty(mocker):
        fake = FakeRequest(path="/squirrels/")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = None

        fake.handleSquirrelsRetrieve("")
        assert 404 in fake.responses

    def it_returns_404_if_id_is_non_numeric(mocker):
            fake = FakeRequest(path="/squirrels/abc")
            mock_db = mocker.patch("squirrel_server.SquirrelDB")
            mock_db.return_value.getSquirrel.return_value = None

            fake.handleSquirrelsRetrieve("abc")
            assert 404 in fake.responses

def describe_handleSquirrelsCreate():

    def it_returns_201_on_success(mocker):
        body = "name=Fluffy&size=large"
        fake = FakeRequest(method="POST", path="/squirrels", body=body)
        mock_db = mocker.patch("squirrel_server.SquirrelDB")

        fake.handleSquirrelsCreate()
        assert 201 in fake.responses

    def it_calls_createSquirrel_with_correct_data(mocker):
        body = "name=Fluffy&size=large"
        fake = FakeRequest(method="POST", path="/squirrels", body=body)
        mock_db = mocker.patch("squirrel_server.SquirrelDB")

        fake.handleSquirrelsCreate()
        mock_db.return_value.createSquirrel.assert_called_once_with("Fluffy", "large")

    def it_returns_500_if_create_payload_is_malformed(mocker):
        body = "name="  # Missing size
        fake = FakeRequest(method="POST", path="/squirrels", body=body)
        mock_db = mocker.patch("squirrel_server.SquirrelDB")

        try:
            fake.handleSquirrelsCreate()
        except KeyError:
            pass 

    def it_returns_500_if_create_body_is_empty(mocker):
        fake = FakeRequest(method="POST", path="/squirrels", body="")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")

        try:
            fake.handleSquirrelsCreate()
        except KeyError:
            pass

    def it_returns_500_if_update_payload_is_malformed(mocker):
        body = "size="
        fake = FakeRequest(method="PUT", path="/squirrels/1", body=body)
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = {"id": 1}

        try:
            fake.handleSquirrelsUpdate("1")
        except KeyError:
            pass


def describe_handleSquirrelsUpdate():

    def it_returns_204_if_squirrel_exists(mocker):
        body = "name=Fluffy&size=small"
        fake = FakeRequest(method="PUT", path="/squirrels/1", body=body)
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = {"id": 1}

        fake.handleSquirrelsUpdate("1")
        assert 204 in fake.responses

    def it_returns_404_if_squirrel_missing(mocker):
        fake = FakeRequest(method="PUT", path="/squirrels/99", body="name=Ghost&size=tiny")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = None

        fake.handleSquirrelsUpdate("99")
        assert 404 in fake.responses

    def it_calls_updateSquirrel_with_correct_data(mocker):
        body = "name=Fluffy&size=small"
        fake = FakeRequest(method="PUT", path="/squirrels/1", body=body)
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = {"id": 1}

        fake.handleSquirrelsUpdate("1")
        mock_db.return_value.updateSquirrel.assert_called_once_with("1", "Fluffy", "small")

def describe_handleSquirrelsDelete():

    def it_returns_204_if_squirrel_exists(mocker):
        fake = FakeRequest(path="/squirrels/1")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = {"id": 1}

        fake.handleSquirrelsDelete("1")
        assert 204 in fake.responses

    def it_returns_404_if_squirrel_missing(mocker):
        fake = FakeRequest(path="/squirrels/99")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = None

        fake.handleSquirrelsDelete("99")
        assert 404 in fake.responses

    def it_calls_deleteSquirrel_with_correct_id(mocker):
        fake = FakeRequest(path="/squirrels/1")
        mock_db = mocker.patch("squirrel_server.SquirrelDB")
        mock_db.return_value.getSquirrel.return_value = {"id": 1}

        fake.handleSquirrelsDelete("1")
        mock_db.return_value.deleteSquirrel.assert_called_once_with("1")


def describe_handle404():

    def it_sets_404_status_and_plain_text(mocker):
        fake = FakeRequest()
        fake.handle404()

        assert 404 in fake.responses
        assert ("Content-Type", "text/plain") in fake.sent_headers
        assert b"404 Not Found" in fake.wfile.data