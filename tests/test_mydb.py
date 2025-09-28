import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from mydb import MyDB

def describe_mydb():

    def it_saves_strings_using_pickle_dump(mocker):
        mocker.patch("os.path.isfile", return_value=True)
        mock_open = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)
        mock_pickle_dump = mocker.patch("pickle.dump")

        db = MyDB("fakefile.db")
        db.saveStrings(["x", "y"])

        mock_open.assert_called_once_with("fakefile.db", "wb")
        mock_pickle_dump.assert_called_once_with(["x", "y"], mock_open.return_value.__enter__.return_value)


    def it_loads_strings_using_pickle_load(mocker):
        mocker.patch("os.path.isfile", return_value=True)
        fake_data = ["a", "b", "c"]
        mock_open = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)
        mock_pickle_load = mocker.patch("pickle.load", return_value=fake_data)

        db = MyDB("fakefile.db")
        result = db.loadStrings()

        mock_open.assert_called_once_with("fakefile.db", "rb")
        mock_pickle_load.assert_called_once()
        assert result == fake_data


    def it_saves_strings_using_pickle_dump_once(mocker):
        mocker.patch("os.path.isfile", return_value=True)

        mock_open = mocker.mock_open()
        open_patch = mocker.patch("builtins.open", mock_open)
        mock_pickle_dump = mocker.patch("pickle.dump")

        db = MyDB("fakefile.db")
        db.saveStrings(["x", "y"])

        open_patch.assert_any_call("fakefile.db", "wb")
        mock_pickle_dump.assert_called_once_with(["x", "y"], mock_open.return_value.__enter__.return_value)


    def it_appends_a_string_and_saves_updated_list(mocker):
        mocker.patch("os.path.isfile", return_value=True)
        mock_loadStrings = mocker.patch("mydb.MyDB.loadStrings", return_value=["first"])
        mock_saveStrings = mocker.patch("mydb.MyDB.saveStrings")

        db = MyDB("fakefile.db")
        db.saveString("second")

        mock_loadStrings.assert_called_once()
        mock_saveStrings.assert_called_once_with(["first", "second"])

