from mock import patch
from mock import Mock
from mongo_python.mongo_create import _post_log_file
import mongo_python.mongo_create


class TestUnitSuite:
    def test_something(self):
        assert True

    def test_selene_create(self):
        assert mongo_python


class TestPostLogFile:
    @patch("selene_python.selene_create.LogFileBuilder")
    def test_gzip_is_called(self, mock_log_file_builder):
        mock_log = Mock()
        intermediate_mock = Mock()
        mock_log_file_builder.return_value.with_output_file.return_value = (
            intermediate_mock
        )
        intermediate_mock.with_receiver.return_value.construct.return_value = mock_log

        _post_log_file("FileName", "ReceiverURL", "LogFileName")

        intermediate_mock.with_receiver.assert_called_once()
        mock_log.gzip_log.assert_called_once_with("LogFileName")
        mock_log.post_log_file.assert_called_once_with("LogFileName")
