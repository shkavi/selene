from datetime import datetime


class Test:
    """
    Test parser for an individual test in a log file.

    Parameters:
        name -- name of a test
        result -- pass/fail result of the test
        branch name -- name of the branch on which the test was run
        build name -- name of the build on which the test was ran
        log -- log file associated with the test
        stage -- name of the testing stage with test was ran in
        critical -- boolean of whether the test was critical or not
        test duration -- time (in seconds) it took the test to run
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        name,
        result,
        branch_name,
        build_name,
        log,
        stage=None,
        critical=True,
        test_duration=None,
    ):
        self._name = name
        self._result = result
        self._branch_name = branch_name
        self._build_name = build_name
        self._log = log
        self._stage = stage
        self._critical = critical
        self._test_duration = test_duration

    @property
    def name(self):
        return self._name

    @property
    def result(self):
        return self._result

    @property
    def branch_name(self):
        return self._branch_name

    @property
    def build_name(self):
        return self._build_name

    @property
    def log(self):
        return self._log

    @property
    def stage(self):
        return self._stage

    @property
    def critical(self):
        return self._critical

    @property
    def test_duration(self):
        return self._test_duration

    def to_json(self):
        items = {}
        items["name"] = self.name
        items["result"] = self.result
        items["branch_name"] = self.branch_name
        items["build_name"] = self.build_name
        items["log"] = self.log
        items["stage"] = self.stage
        items["critical"] = self.critical
        items["test_duration"] = self.test_duration
        return {k: v for k, v in items.items() if v is not None}

    def parse_test(self, test, prefix):
        self._name = self._get_test_name(test, prefix)
        self._result = test.find("status").get("status").lower()
        if self._result == "skip":
            self._result = "fail"
        self._critical = self._get_critical_value(test)
        self._test_duration = self._get_test_duration(test)
        return self.to_json()

    def _get_test_name(self, test, prefix):
        name = test.get("name")
        return "{0}.{1}".format(prefix, name)

    def _get_critical_value(self, test):
        status_attrib = test.find("status")
        if (
            status_attrib.get("status").lower() == "skip"
            or status_attrib.get("critical", "yes").lower() == "no"
        ):
            return False
        return True

    def _get_test_duration(self, test):
        executed_at = datetime.strptime(
            test.find("status").get("starttime"), "%Y%m%d %H:%M:%S.%f"
        )
        completed_at = datetime.strptime(
            test.find("status").get("endtime"), "%Y%m%d %H:%M:%S.%f"
        )
        return (completed_at - executed_at).total_seconds()

    def get_name(self):
        return self._name


class TestBuilder:
    """
    Helper class for parsing a test.
    """

    def __init__(self):
        self._name = None
        self._result = None
        self._branch_name = None
        self._build_name = None
        self._log = None
        self._stage = None
        self._critical = None
        self._test_duration = None

    def with_name(self, name):
        self._name = name
        return self

    def with_result(self, result):
        self._result = result
        return self

    def with_branch_name(self, branch_name):
        self._branch_name = branch_name
        return self

    def with_build_name(self, build_name):
        self._build_name = build_name
        return self

    def with_log(self, log):
        self._log = log
        return self

    def with_stage(self, stage):
        self._stage = stage
        return self

    def with_critical(self, critical):
        self._critical = critical
        return self

    def with_test_duration(self, test_duration):
        self._test_duration = test_duration
        return self

    def construct(self):
        return Test(
            self._name,
            self._result,
            self._branch_name,
            self._build_name,
            self._log,
            self._stage,
            self._critical,
            self._test_duration,
        )
