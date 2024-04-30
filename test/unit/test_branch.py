import pytest
from hamcrest import assert_that, equal_to, instance_of, is_, is_not

from mongo_python.branch import Branch, BranchBuilder, BranchNotFoundError


def create_branch():
    return BranchBuilder().with_name("master").construct()


# pylint: disable=too-few-public-methods
class TestBranchBuilder:
    def test_create_branch(self):
        branch = create_branch()

        assert_that(branch, is_(instance_of(Branch)))
        assert_that(branch.name, is_(equal_to("master")))


class TestBranch:
    attributes = ["name"]
    values = [("name", "master")]

    def test_compare(self):
        branch = create_branch()
        assert_that(branch, is_(equal_to(branch)))
        assert_that(branch, is_(equal_to(Branch("master"))))
        assert_that(branch, is_not(equal_to(Branch("release"))))

    @pytest.mark.parametrize("attribute,value", values, ids=attributes)
    def test_get_attribute(self, attribute, value):
        branch = create_branch()
        assert_that(getattr(branch, attribute), is_(equal_to(value)))

    def test_to_json(self):
        branch = create_branch()
        json = branch.to_json()
        expected = {"name": "master"}
        assert_that(json, is_(equal_to(expected)))


# pylint: disable=too-few-public-methods
class TestBranchNotFoundError:
    def test_throw_error(self):
        branch = create_branch()
        expected = "Error not found: Branch: master"
        with pytest.raises(BranchNotFoundError, match=expected):
            raise BranchNotFoundError(branch)
