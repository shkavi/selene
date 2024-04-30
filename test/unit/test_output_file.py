import json
import pytest
from hamcrest import assert_that, equal_to, instance_of, is_

from mongo_python.output_file import (
    OutputFile,
    OutputFileBuilder,
    _parse_robot,
    _parse_not_robot,
)


def create_output_file(filename="output.xml"):
    return OutputFileBuilder().with_filename(filename).construct()


# pylint: disable=too-few-public-methods
class TestOutputFileBuilder:
    def test_create_output_file(self):
        output_file = create_output_file()

        assert_that(output_file, is_(instance_of(OutputFile)))
        assert_that(output_file.filename, is_(equal_to("output.xml")))

    @pytest.mark.parametrize(
        "filename,parser",
        [
            ("output.xml", _parse_robot),
            ("TESTS-project.xml", _parse_not_robot),
            ("pytest_xUnit.xml", _parse_not_robot),
            ("gtest_xUnit.xml", _parse_not_robot),
        ],
    )
    def test_construct_robot(self, filename, parser):
        builder = OutputFileBuilder().with_filename(filename)
        output_file = builder.construct()
        assert_that(
            id(output_file.parse_output_file_function), is_(equal_to(id(parser)))
        )


class TestOutputFile:
    def test_filename(self):
        output_file = create_output_file()
        result = output_file.filename
        assert_that(result, is_(equal_to("output.xml")))

    def test_tests(self):
        output_file = create_output_file()
        result = output_file.tests
        assert_that(result, is_(equal_to([])))

    def test_get_tests(self):
        output_file = create_output_file()
        result = output_file.get_tests()
        assert_that(result, is_(equal_to([])))

    @pytest.mark.parametrize(
        "filename",
        [
            ("test/data/output.xml"),
            ("test/data/TESTS-project.xml"),
            ("test/data/pytest_xUnit.xml"),
            ("test/data/gtest_xUnit.xml"),
        ],
    )
    def test_parse_robot_test(self, filename):
        output_file = create_output_file(filename)
        with open(filename + ".json") as f:
            expected = json.loads(f.read())
        output_file.parse_output_file()
        result = output_file.get_tests()
        assert_that(result, is_(equal_to(expected)))
