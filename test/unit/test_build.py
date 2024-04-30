import pytest
from hamcrest import assert_that, equal_to, instance_of, is_

from mongo_python.branch import Branch
from mongo_python.build import Build, BuildBuilder, BuildNotFoundError


def create_build():
    return (
        BuildBuilder()
        .with_name("product")
        .with_id(4)
        .with_branch_name("master")
        .with_status("SUCCESS")
        .with_pipeline_status("SUCCESS")
        .construct()
    )


class TestBuildBuilder:
    def test_create_min_build(self):
        build = create_build()

        assert_that(build, is_(instance_of(Build)))
        assert_that(build.name, is_(equal_to("product")))
        assert_that(build.branch.name, is_(equal_to("master")))

    def test_throw_error_if_not_min_build(self):
        with pytest.raises(AssertionError):
            BuildBuilder().construct()

    def test_create_full_build(self):
        build = (
            BuildBuilder()
            .with_name("product")
            .with_id(4)
            .with_branch_name("master")
            .with_status("SUCCESS")
            .with_pipeline_status("SUCCESS")
            .construct()
        )

        assert_that(build, is_(instance_of(Build)))
        assert_that(build.name, is_(equal_to("product")))
        assert_that(build.build_id, is_(equal_to(4)))
        assert_that(build.branch.name, is_(equal_to("master")))
        assert_that(build.status, is_(equal_to("SUCCESS")))
        assert_that(build.pipeline_status, is_(equal_to("SUCCESS")))


class TestBuild:
    attributes = ["name", "build_id", "branch", "status", "pipeline_status"]
    attribute_value_pairs = [
        ("name", "product"),
        ("build_id", 4),
        ("branch", Branch("master")),
        ("status", "SUCCESS"),
        ("pipeline_status", "SUCCESS"),
    ]

    @pytest.mark.parametrize("attribute,value", attribute_value_pairs, ids=attributes)
    def test_get_attribute(self, attribute, value):
        build = create_build()
        assert_that(getattr(build, attribute), is_(equal_to(value)))

    def test_to_json(self):
        build = create_build()
        json = build.to_json()
        expected = {
            "name": "product",
            "build_id": 4,
            "branch_name": "master",
            "status": "SUCCESS",
            "pipeline_status": "SUCCESS",
        }
        assert_that(json, is_(equal_to(expected)))


# pylint: disable=too-few-public-methods
class TestBuildNotFoundError:
    def test_throw_error(self):
        build = create_build()
        expected = "Error not found: Branch: master on Build: product"
        with pytest.raises(BuildNotFoundError, match=expected):
            raise BuildNotFoundError(build)
