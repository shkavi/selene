class Branch:
    """
    Model for a software branch.

    Parameters:
        name -- branch name
    """

    def __init__(self, name):
        self._name = name

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def name(self):
        return self._name

    def to_json(self):
        items = {}
        items["name"] = self.name
        return {k: v for k, v in items.items() if v is not None}


class BranchBuilder:
    """
    Helper class for creating software branch objects.
    """

    def __init__(self):
        self._name = None

    def with_name(self, name):
        self._name = name
        return self

    def construct(self):
        assert self._name is not None
        return Branch(self._name)


class BranchNotFoundError(Exception):
    """
    Raised when a branch lookup fails.

    Parameters:
        branch -- branch that was not found
    """

    def __init__(self, branch):
        msg = "Error not found: Branch: {}".format(branch.name)
        super().__init__(msg)
