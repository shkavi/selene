import xml.etree.ElementTree as ET
from .test import TestBuilder


def _parse_robot(output_xml_root):
    suite = output_xml_root.find("suite")
    for test in _parse_robot_suite(suite):
        yield test


def _parse_not_robot(suites):
    for item in suites.iter():
        if item.tag == "testcase":
            yield TestBuilder().with_name(
                item.get("classname") + "." + item.get("name")
            ).with_result(
                "fail"
                if item.findall("skipped")
                or item.findall("failure")
                or item.get("status") == "skipped"
                or item.get("status") == "failure"
                else "pass"
            ).with_critical(
                item.get("status") != "skipped" and not item.findall("skipped")
            ).with_test_duration(
                float(item.get("time"))
            ).construct().to_json()


def _parse_robot_suite(suite, parent_name=None):
    test_builder = TestBuilder().construct()
    if parent_name:
        suite_name = "{}.{}".format(parent_name, suite.get("name"))
    else:
        suite_name = suite.get("name")
    for test in suite.findall("test"):
        yield test_builder.parse_test(test, suite_name)
    for subsuite in suite.findall("suite"):
        for test in _parse_robot_suite(subsuite, suite_name):
            yield test


class OutputFile:
    """
    Model for an individual output file.

    Parameters:
        filename -- name of the output file
        tests -- a list of the tests parsed from the output file. Starts empty.
        output_file_parse_function --  a function that takes output xml root
            and returns a list of tests
    """

    def __init__(self, filename, parse_output_file_function=_parse_robot):
        self._filename = filename
        self._tests = []
        self.parse_output_file_function = parse_output_file_function

    @property
    def filename(self):
        return self._filename

    @property
    def tests(self):
        return self._tests

    def parse_output_file(self):
        root = ET.parse(self._filename).getroot()
        self._tests = list(self.parse_output_file_function(root))

    def get_tests(self):
        return self._tests


class OutputFileBuilder:
    """
    Helper class for building output file objects.
    """

    def __init__(self):
        self._filename = None

    def with_filename(self, filename):
        self._filename = filename
        return self

    def construct(self):
        return OutputFile(self._filename, self.__get_parser())

    def __get_parser(self):
        not_robot_parsable = ["TESTS-", "pytest_xUnit.xml", "gtest_xUnit.xml"]
        parser = (
            _parse_not_robot
            for substring in not_robot_parsable
            if substring in self._filename
        )
        return next(parser, _parse_robot)
