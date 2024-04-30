import xml.etree.ElementTree as ET
import pytest
from hamcrest import assert_that, equal_to, instance_of, is_

from mongo_python.test import Test as _Test, TestBuilder as _TestBuilder


def create_test():
    return (
        _TestBuilder()
        .with_name("suite.test")
        .with_result("pass")
        .with_build_name("bar")
        .with_log("log_file.log")
        .with_stage("One")
        .with_critical(True)
        .with_test_duration(1.3)
        .construct()
    )


# pylint: disable=too-few-public-methods
class TestTestBuilder:
    def test_create_test(self):
        test = create_test()

        assert_that(test, is_(instance_of(_Test)))
        assert_that(test.name, is_(equal_to("suite.test")))
        assert_that(test.result, is_(equal_to("pass")))
        assert_that(test.build_name, is_(equal_to("bar")))
        assert_that(test.log, is_(equal_to("log_file.log")))
        assert_that(test.stage, is_(equal_to("One")))
        assert_that(test.critical, is_(equal_to(True)))
        assert_that(test.test_duration, is_(equal_to(1.3)))


class TestTest:
    attributes = [
        "name",
        "result",
        "build_name",
        "log",
        "stage",
        "critical",
        "test_duration",
    ]
    attribute_value_pairs = [
        ("name", "suite.test"),
        ("result", "pass"),
        ("build_name", "bar"),
        ("log", "log_file.log"),
        ("stage", "One"),
        ("critical", True),
        ("test_duration", 1.3),
    ]

    @pytest.mark.parametrize("attribute,value", attribute_value_pairs, ids=attributes)
    def test_get_attribute(self, attribute, value):
        test = create_test()
        assert_that(getattr(test, attribute), is_(equal_to(value)))

    def test_to_json(self):
        test = create_test()
        json = test.to_json()
        expected = {
            "name": "suite.test",
            "result": "pass",
            "build_name": "bar",
            "log": "log_file.log",
            "stage": "One",
            "critical": True,
            "test_duration": 1.3,
        }
        assert_that(json, is_(equal_to(expected)))

    def test_parse_test(self):
        test = create_test()
        sample_test = ET.fromstring(
            "<test name='test'><status status='pass' \
                             endtime='20180826 04:43:02.239' critical='yes' \
                             starttime='20180826 04:43:00.939'> \
                             </status></test>"
        )
        prefix = "suite"
        json = test.parse_test(sample_test, prefix)
        expected = {
            "name": "suite.test",
            "result": "pass",
            "build_name": "bar",
            "log": "log_file.log",
            "stage": "One",
            "critical": True,
            "test_duration": 1.3,
        }
        assert_that(json, is_(equal_to(expected)))

    def test_get_critical_value_when_false(self):
        test = create_test()
        sample_test = ET.fromstring(
            "<test name='test'><status status='pass' \
                             endtime='20180826 04:43:02.239' critical='no' \
                             starttime='20180826 04:43:00.939'> \
                             </status></test>"
        )
        # pylint: disable=protected-access
        result = test._get_critical_value(sample_test)
        assert_that(result, is_(equal_to(False)))

    def test_get_name(self):
        test = create_test()
        result = test.get_name()
        assert_that(result, is_(equal_to("suite.test")))
