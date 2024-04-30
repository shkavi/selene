from mock import patch, Mock
import pytest
from requests import RequestException
from hamcrest import assert_that, equal_to, instance_of, is_, is_not

from mongo_python.test import TestBuilder as _TestBuilder
from mongo_python.build import BuildBuilder, BuildNotFoundError
from mongo_python.branch import BranchBuilder, BranchNotFoundError
from mongo_python.selene_server import (
    SeleneRequestError,
    SeleneServer,
    SeleneServerBuilder,
)
from mongo_python.server import Server


def create_selene_server():
    return SeleneServerBuilder().with_url("http://skydocker.adtran.com").construct()


def create_build():
    return (
        BuildBuilder()
        .with_name("build-name")
        .with_id(4)
        .with_branch_name("branch-name")
        .with_status("SUCCESS")
        .with_pipeline_status("SUCCESS")
        .construct()
    )


def create_mock_builds_response():
    mock = Mock()
    mock.response = [
        {
            "build_id": 9000,
            "name": "product",
            "created_at": "2018-01-01 01:00:00",
            "branch_name": "branch-name",
            "branch_id": 4200,
            "status": "SUCCESS",
            "pipeline_status": "SUCCESS",
        },
        {
            "build_id": 4,
            "name": "build-name",
            "created_at": "2018-01-01 02:00:00",
            "branch_name": "branch-name",
            "branch_id": 4201,
            "status": "SUCCESS",
            "pipeline_status": "SUCCESS",
        },
    ]
    return mock


def create_mock_branches_response():
    mock = Mock()
    mock.response = [
        {
            "branch_id": 9000,
            "name": "branch-name",
            "created_at": "2018-01-01 01:00:00",
            "art_name": "smart",
            "art_id": 420,
            "pipeline_url": "www.greenpipelines.com",
            "alias": "green",
        },
        {
            "branch_id": 9001,
            "name": "super-branch-name",
            "created_at": "2018-01-01 02:00:00",
            "art_name": "smart",
            "art_id": 420,
            "pipeline_url": "www.greenpipelines.com",
            "alias": "supergreen",
        },
    ]
    return mock


# pylint: disable=too-few-public-methods
class TestSeleneServerBuilder:
    def test_create_server(self):
        selene_server = create_selene_server()
        assert_that(selene_server, is_(instance_of(Server)))
        assert_that(selene_server, is_(instance_of(SeleneServer)))
        assert_that(selene_server.url, is_(equal_to("http://skydocker.adtran.com")))


class TestSeleneServer:
    def test_get_builds(self):
        selene_server = create_selene_server()
        mock_builds_response = create_mock_builds_response()
        with patch.object(
            selene_server,
            "make_get_request",
            return_value=mock_builds_response.response,
        ) as mock_request:
            builds = selene_server.get_builds()

        assert_that(builds, is_not(None))
        mock_request.assert_called_once_with("http://skydocker.adtran.com/api/build")

    def test_get_builds_not_found(self):
        selene_server = create_selene_server()
        with patch.object(selene_server, "make_get_request") as mock_request:
            mock_request.side_effect = RequestException()
            with pytest.raises(SeleneRequestError):
                selene_server.get_builds()

    def test_get_build_id(self):
        selene_server = create_selene_server()
        mock_builds_response = create_mock_builds_response()
        build = create_build()

        with patch.object(
            selene_server,
            "make_get_request",
            return_value=mock_builds_response.response,
        ):
            build_id = selene_server.get_build_id(build)

        assert_that(build_id, is_(equal_to(4)))

    def test_get_build_id_build_not_found(self):
        selene_server = create_selene_server()
        mock_builds_response = create_mock_builds_response()
        build = (
            BuildBuilder()
            .with_name("unknown-build")
            .with_branch_name("branch-name")
            .construct()
        )

        with patch.object(
            selene_server,
            "make_get_request",
            return_value=mock_builds_response.response,
        ):
            with pytest.raises(BuildNotFoundError):
                selene_server.get_build_id(build)

    def test_create_build(self):
        selene_server = create_selene_server()
        build = create_build()
        with patch.object(selene_server, "get_branch_id", return_value=1):
            with patch.object(
                selene_server, "send_to_api", return_value=Mock()
            ) as mock_request:
                selene_server.create_build(build)

        mock_request.assert_called_once_with(
            "post",
            "http://skydocker.adtran.com/api/build",
            {
                "name": "build-name",
                "build_id": 4,
                "branch_name": "branch-name",
                "status": "SUCCESS",
                "pipeline_status": "SUCCESS",
            },
        )

    def test_create_build_branch_not_found(self):
        selene_server = create_selene_server()
        build = create_build()
        with patch.object(selene_server, "get_branch_id") as mock_response:
            mock_response.side_effect = BranchNotFoundError(build.branch)
            with patch.object(selene_server, "_make_post_request") as mock_request:
                selene_server.create_build(build)

        mock_request.assert_called_with(
            "http://skydocker.adtran.com/api/build",
            {
                "name": "build-name",
                "build_id": 4,
                "branch_name": "branch-name",
                "status": "SUCCESS",
                "pipeline_status": "SUCCESS",
            },
        )

    def test_create_build_request_error(self):
        selene_server = create_selene_server()
        build = create_build()
        with patch.object(selene_server, "get_branch_id", return_value=1):
            with patch.object(selene_server, "_make_post_request") as mock_request:
                mock_request.side_effect = RequestException()
                with pytest.raises(SeleneRequestError):
                    selene_server.create_build(build)

    def test_update_build(self):
        selene_server = create_selene_server()
        build = create_build()
        with patch.object(
            selene_server, "send_to_api", return_value=Mock()
        ) as mock_request:
            selene_server.update_build(build)

        mock_request.assert_called_once_with(
            "patch",
            "http://skydocker.adtran.com/api/build/4",
            {
                "name": "build-name",
                "build_id": 4,
                "branch_name": "branch-name",
                "status": "SUCCESS",
                "pipeline_status": "SUCCESS",
            },
        )

    def test_get_branches(self):
        selene_server = create_selene_server()
        mock_branches_response = create_mock_branches_response()
        with patch.object(
            selene_server,
            "make_get_request",
            return_value=mock_branches_response.response,
        ) as mock_request:
            branches = selene_server.get_branches()

        assert_that(branches, is_not(None))
        mock_request.assert_called_once_with("http://skydocker.adtran.com/api/branch")

    def test_get_branches_request_error(self):
        selene_server = create_selene_server()
        with patch.object(selene_server, "make_get_request") as mock_request:
            mock_request.side_effect = RequestException()
            with pytest.raises(SeleneRequestError):
                selene_server.get_branches()

    def test_get_branch_id(self):
        selene_server = create_selene_server()
        mock_branches_response = create_mock_branches_response()
        branch = BranchBuilder().with_name("super-branch-name").construct()

        with patch.object(
            selene_server,
            "make_get_request",
            return_value=mock_branches_response.response,
        ):
            branch_id = selene_server.get_branch_id(branch)

        assert_that(branch_id, is_(equal_to(9001)))

    def test_get_branch_id_branch_not_found(self):
        selene_server = create_selene_server()
        mock_branches_response = create_mock_branches_response()
        branch = BranchBuilder().with_name("ssj-branch").construct()

        with patch.object(
            selene_server,
            "make_get_request",
            return_value=mock_branches_response.response,
        ):
            with pytest.raises(BranchNotFoundError):
                selene_server.get_branch_id(branch)

    def test_create_branch(self):
        selene_server = create_selene_server()
        branch = BranchBuilder().with_name("ssj-branch").construct()

        with patch.object(
            selene_server, "send_to_api", return_value=Mock()
        ) as mock_request:
            selene_server.create_branch(branch)

        mock_request.assert_called_once_with(
            "post", "http://skydocker.adtran.com/api/branch", {"name": "ssj-branch"}
        )

    def test_create_branch_request_error(self):
        selene_server = create_selene_server()
        branch = BranchBuilder().with_name("ssj-branch").construct()

        with patch.object(selene_server, "_make_post_request") as mock_request:
            mock_request.side_effect = RequestException()
            with pytest.raises(SeleneRequestError):
                selene_server.create_branch(branch)

    def test_create_test_case(self):
        selene_server = create_selene_server()
        test = (
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

        with patch.object(
            selene_server, "send_to_api", return_value=Mock()
        ) as mock_request:
            selene_server.create_test_case(test)

        mock_request.assert_called_once_with(
            "post",
            "http://skydocker.adtran.com/api/testcase",
            {
                "name": "suite.test",
                "result": "pass",
                "build_name": "bar",
                "log": "log_file.log",
                "stage": "One",
                "critical": True,
                "test_duration": 1.3,
            },
        )

    def test_create_test_case_request_error(self):
        selene_server = create_selene_server()
        test = (
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

        with patch.object(selene_server, "_make_post_request") as mock_request:
            mock_request.side_effect = RequestException()
            with pytest.raises(SeleneRequestError):
                selene_server.create_test_case(test)

    def test_create_test_result(self):
        selene_server = create_selene_server()
        test = (
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

        with patch.object(
            selene_server, "send_to_api", return_value=Mock()
        ) as mock_request:
            selene_server.create_test_result(test)

        mock_request.assert_called_once_with(
            "post",
            "http://skydocker.adtran.com/api/test-result",
            {
                "name": "suite.test",
                "result": "pass",
                "build_name": "bar",
                "log": "log_file.log",
                "stage": "One",
                "critical": True,
                "test_duration": 1.3,
            },
        )

    def test_create_test_result_request_error(self):
        selene_server = create_selene_server()
        test = (
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

        with patch.object(selene_server, "_make_post_request") as mock_request:
            mock_request.side_effect = RequestException()
            with pytest.raises(SeleneRequestError):
                selene_server.create_test_result(test)


# pylint: disable=too-few-public-methods
class TestSeleneRequestError:
    def test_throw_error(self):
        expected = "Error: Get Error"
        with pytest.raises(SeleneRequestError, match=expected):
            raise SeleneRequestError("Get Error")
