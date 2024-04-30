import requests


class Server:
    """
    Model for a server.

    Parameters:
        url -- the url the server is running
    """

    def __init__(self, url):
        self._url = url

    @property
    def url(self):
        return self._url

    def make_get_request(self, api):
        response = requests.get(api)
        response.raise_for_status()
        return response.json()

    def _make_post_request(self, api, data):
        self.send_to_api("post", api, data)

    def _make_patch_request(self, api, data):
        self.send_to_api("patch", api, data)

    def send_to_api(self, method, api, data):
        headers = {"content-type": "application/json"}
        response = requests.request(method=method, url=api, json=data, headers=headers)
        response.raise_for_status()
        return response


class ServerBuilder:
    """
    Helper class for building server objects.
    """

    def __init__(self):
        self._url = None

    def with_url(self, url):
        self._url = url
        return self

    def construct(self):
        assert self._url is not None
        return Server(self._url)
