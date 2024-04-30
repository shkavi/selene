from .branch import BranchBuilder


class Build:
    """
    Model for an individual build for a branch.

    Parameters:
       name -- build name
       build_id -- build id
       branch -- branch object
       status -- build status reported by Jenkins
       pipeline status -- build status to pass smoke check
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self, name, build_id=None, branch=None, status=None, pipeline_status=None
    ):
        self._name = name
        self.build_id = build_id
        self._branch = branch
        self._status = status
        self._pipeline_status = pipeline_status

    @property
    def name(self):
        return self._name

    @property
    def branch(self):
        return self._branch

    @property
    def status(self):
        return self._status

    @property
    def pipeline_status(self):
        return self._pipeline_status

    def to_json(self):
        items = {}
        items["name"] = self.name
        items["build_id"] = self.build_id
        items["branch_name"] = self.branch.name
        items["status"] = self.status
        items["pipeline_status"] = self.pipeline_status
        return {k: v for k, v in items.items() if v is not None}


class BuildBuilder:
    """
    Helper class for building software build objects.
    """

    def __init__(self):
        self._name = None
        self._id = None
        self._branch = None
        self._status = None
        self._pipeline_status = None

    def with_name(self, name):
        self._name = name
        return self

    def with_id(self, build_id):
        self._id = build_id
        return self

    def with_branch_name(self, branch_name):
        self._branch = BranchBuilder().with_name(branch_name).construct()
        return self

    def with_status(self, status):
        self._status = status
        return self

    def with_pipeline_status(self, status):
        self._pipeline_status = status
        return self

    def construct(self):
        assert self._name and self._branch is not None
        return Build(
            self._name, self._id, self._branch, self._status, self._pipeline_status
        )


class BuildNotFoundError(Exception):
    """
    Raised when a build lookup fails.

    Parameters:
        build -- build that was not found
    """

    def __init__(self, build):
        msg = "Error not found: Branch: {} on Build: {}".format(
            build.branch.name, build.name
        )
        super().__init__(msg)
