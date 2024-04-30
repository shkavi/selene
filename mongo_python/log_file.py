import os
import requests
import gzip


class LogFile:
    """
    Model for an individual log file.

    Parameters:
        output file -- output file from which the log file name is derived
        receiver -- the url the server is running
        log path -- full path to the log file. Starts empty
        log file -- name of the log file saved to the server. Starts empty
    """

    def __init__(self, output_file, receiver):
        self._output_file = output_file
        self._receiver = receiver
        self._log_path = None
        self._log_file = None

    @property
    def output_file(self):
        return self._output_file

    @property
    def receiver(self):
        return self._receiver

    @property
    def log_path(self):
        return self._log_path

    @property
    def log_file(self):
        return self._log_file

    def post_log_file(self, log_path=""):
        """
        Post the log file
        if the log_path is None or empty, we'll try to autodetect the log file
        based on the output file
        """
        self._log_path = log_path if log_path else self._get_log_path()

        if os.path.isfile(self._log_path):
            self._post_log()

    def gzip_log(self, file=""):
        file = file if file else self._get_log_path()
        if not os.path.isfile(file):
            return
        with open(file, "rb") as fp:
            data = fp.read()
            bindata = bytearray(data)
        with gzip.open(file, "wb") as f:
            f.write(bindata)

    def _get_log_path(self):
        log = self._output_file.split("output")
        return os.path.join(log[0] + "log.html")

    def _post_log(self):
        url = self._receiver + "/api/log/upload"
        if os.path.isfile(self._log_path):
            with open(self._log_path, "rb") as fin:
                files = {"file": fin}
                res = requests.post(url=url, files=files)
                self._log_file = res.text


class LogFileBuilder:
    """
    Helper class for building log file objects.
    """

    def __init__(self):
        self._output_file = None
        self._receiver = None
        self._log_path = None
        self._log_file = None

    def with_output_file(self, output_file):
        self._output_file = output_file
        return self

    def with_receiver(self, receiver):
        self._receiver = receiver
        return self

    def construct(self):
        return LogFile(self._output_file, self._receiver)


class LogFileNotFoundError(Exception):
    """
    Raised when a log file is not found in the given path

    Parameters:
        log path -- path where the log was not found
    """

    def __init__(self, log_path):
        msg = "Error not found: No file found in path: {0}".format(log_path)
        super().__init__(msg)
