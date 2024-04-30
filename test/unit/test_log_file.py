import os
import pytest
from hamcrest import assert_that, equal_to, instance_of, is_, calling
from mock import patch
from mock import mock_open

from mongo_python.log_file import LogFile, LogFileBuilder, LogFileNotFoundError


def create_log_file():
    return (
        LogFileBuilder()
        .with_output_file("output.xml")
        .with_receiver("http://skydocker.adtran.com")
        .construct()
    )


# pylint: disable=too-few-public-methods
class TestLogFileBuilder:
    def test_create_log_file(self):
        log = create_log_file()

        assert_that(log, is_(instance_of(LogFile)))
        assert_that(log.output_file, is_("output.xml"))
        assert_that(log.receiver, is_("http://skydocker.adtran.com"))
        assert_that(log.log_path, is_(None))
        assert_that(log.log_file, is_(None))


class TestLogFile:
    attributes = ["output_file", "receiver", "log_path", "log_file"]
    attribute_value_pairs = [
        ("output_file", "output.xml"),
        ("receiver", "http://skydocker.adtran.com"),
        ("log_path", None),
        ("log_file", None),
    ]

    @pytest.mark.parametrize("attribute,value", attribute_value_pairs, ids=attributes)
    def test_get_attribute(self, attribute, value):
        log_file = create_log_file()
        assert_that(getattr(log_file, attribute), is_(equal_to(value)))

    def test_get_log_path(self):
        log_file = create_log_file()
        # pylint: disable=protected-access
        assert_that(log_file._get_log_path(), is_("log.html"))

    def test_post_log_if_exists(self):
        log_file = create_log_file()
        file = open("log.html", "w")
        file.write("I am a log file")
        file.close()
        # pylint: disable=protected-access
        log_file._log_path = "log.html"
        # pylint: disable=protected-access
        log_file._post_log()
        os.remove("log.html")
        assert_that(calling(log_file._post_log))

    def test_post_log_if_not_exists(self):
        log_file = create_log_file()
        # pylint: disable=protected-access
        log_file._log_path = "log.html"
        # pylint: disable=protected-access
        log_file._post_log()
        assert_that(calling(log_file._post_log))

    def test_post_log_file_if_exists(self):
        log_file = create_log_file()
        file = open("log.html", "w")
        file.write("I am a log file")
        file.close()
        # pylint: disable=protected-access
        log_file._log_path = "log.html"
        log_file.post_log_file()
        os.remove("log.html")
        assert_that(calling(log_file.post_log_file))
        assert_that(log_file._get_log_path(), is_("log.html"))

    def test_post_log_file_if_not_exists(self):
        log_file = create_log_file()
        log_file.post_log_file()
        assert_that(calling(log_file.post_log_file))

    @patch("selene_python.log_file.os")
    @patch.object(LogFile, "_get_log_path")
    @patch("builtins.bytearray")
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    @patch("selene_python.log_file.gzip")
    def test_gzip_log(
        self, mock_gzip, mock_open_file, mock_bytearray, mock_get_path, mock_os
    ):
        log_file = LogFile("output_file", "receiver")

        log_file.gzip_log("log_file")

        mock_gzip.open.assert_called_once_with("log_file", "wb")

    @patch("selene_python.log_file.os")
    @patch.object(LogFile, "_get_log_path")
    @patch("builtins.bytearray")
    @patch("builtins.open", new_callable=mock_open, read_data="filedata")
    @patch("selene_python.log_file.gzip")
    def test_gzip_log_bytearray(
        self, mock_gzip, mock_open_file, mock_bytearray, mock_get_path, mock_os
    ):
        log_file = LogFile("output_file", "receiver")

        log_file.gzip_log("log_file")

        mock_bytearray.assert_called_once_with("filedata")

    @patch("selene_python.log_file.os")
    @patch.object(LogFile, "_get_log_path")
    @patch("builtins.bytearray")
    @patch("builtins.open", new_callable=mock_open, read_data="filedata")
    @patch("selene_python.log_file.gzip")
    def test_gzip_log_no_path(
        self, mock_gzip, mock_open_file, mock_bytearray, mock_get_path, mock_os
    ):
        mock_get_path.return_value = "GeneratedPath"
        log_file = LogFile("output_file", "receiver")
        mock_os.path.isfile.return_value = False

        log_file.gzip_log(None)

        mock_get_path.assert_called_once()
        mock_gzip.assert_not_called()
        mock_open_file.assert_not_called()
        mock_bytearray.assert_not_called()
        mock_os.path.isfile.assert_called_once_with("GeneratedPath")


# pylint: disable=too-few-public-methods
class TestLogFileNotFoundError:
    def test_throw_error(self):
        expected = "Error not found: No file found in path: test_results/log.html"
        with pytest.raises(LogFileNotFoundError, match=expected):
            raise LogFileNotFoundError("test_results/log.html")
