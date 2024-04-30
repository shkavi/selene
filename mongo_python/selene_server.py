from requests import RequestException

from .build import BuildNotFoundError
from .branch import BranchNotFoundError
from .server import Server, ServerBuilder


class SeleneServer(Server):
    """
    Model for a selene server.

    Parameters:
        url -- the url the server is running
    """

    def get_builds(self):
        api_call = "{0}/api/build".format(self.url)

        try:
            builds = self.make_get_request(api_call)
        except RequestException as exception:
            raise SeleneRequestError(exception) from exception

        return builds

    def get_build_id(self, build):
        builds = self.get_builds()

        try:
            return next(
                b["build_id"]
                for b in builds
                if b["name"] == build.name and b["branch_name"] == build.branch.name
            )
        except StopIteration as exception:
            raise BuildNotFoundError(build) from exception

    def create_build(self, build):
        try:
            self.get_branch_id(build.branch)
        except BranchNotFoundError:
            self.create_branch(build.branch)

        api_call = "{0}/api/build".format(self.url)

        try:
            self._make_post_request(api_call, build.to_json())
        except RequestException as exception:
            raise SeleneRequestError(exception) from exception

    def update_build(self, build):
        api_call = "{0}/api/build/{1}".format(self.url, build.build_id)
        self._make_patch_request(api_call, build.to_json())

    def get_branches(self):
        api_call = "{0}/api/branch".format(self.url)

        try:
            branches = self.make_get_request(api_call)
        except RequestException as exception:
            raise SeleneRequestError(exception) from exception

        return branches

    def get_branch_id(self, branch):
        branches = self.get_branches()

        try:
            return next(b["branch_id"] for b in branches if b["name"] == branch.name)
        except StopIteration as exception:
            raise BranchNotFoundError(branch) from exception

    def create_branch(self, branch):
        call_api = "{0}/api/branch".format(self.url)
        try:
            self._make_post_request(call_api, branch.to_json())
        except RequestException as exception:
            raise SeleneRequestError(exception) from exception

    def create_test_case(self, test):
        call_api = "{0}/api/testcase".format(self.url)
        try:
            self._make_post_request(call_api, test.to_json())
        except RequestException as exception:
            raise SeleneRequestError(exception) from exception

    def create_test_result(self, test):
        call_api = "{0}/api/test-result".format(self.url)
        try:
            self._make_post_request(call_api, test.to_json())
        except RequestException as exception:
            raise SeleneRequestError(exception) from exception


class SeleneServerBuilder(ServerBuilder):
    """
    Helper class for creating selene server objects.
    """

    def construct(self):
        assert self._url is not None
        return SeleneServer(self._url)


class SeleneRequestError(Exception):
    """
    Raised when communication to the selene server fails.

    Parameters:
        error -- Request error raised by the requests library.
    """

    def __init__(self, error):
        msg = "Error: {0}".format(error)
        super().__init__(msg)
