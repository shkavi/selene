import pytest
import requests
import httpretty
from hamcrest import assert_that, equal_to, instance_of, is_

from mongo_python.server import Server, ServerBuilder


def create_server():
    return ServerBuilder().with_url("http://skydocker.adtran.com").construct()


# pylint: disable=too-few-public-methods
class TestServerBuilder:
    def test_create_server(self):
        server = create_server()

        assert_that(server, is_(instance_of(Server)))
        assert_that(server.url, is_(equal_to("http://skydocker.adtran.com")))


class TestServer:
    attributes = ["url"]
    attribute_value_pairs = [("url", "http://skydocker.adtran.com")]

    @pytest.mark.parametrize("attribute,value", attribute_value_pairs, ids=attributes)
    def test_get_attribute(self, attribute, value):
        server = create_server()
        assert_that(getattr(server, attribute), is_(equal_to(value)))

    def test_make_get_request(self):
        server = create_server()
        httpretty.enable()
        httpretty.register_uri(
            httpretty.GET,
            "http://skydocker.adtran.com/api/build",
            body='{"name": "foobar"}',
        )
        response = server.make_get_request("http://skydocker.adtran.com/api/build")
        response = requests.get("http://skydocker.adtran.com/api/build")
        assert_that(response.status_code, is_(equal_to(200)))
        assert_that(response.json(), is_(equal_to({"name": "foobar"})))
        httpretty.disable()

    def test_post_to_api_request(self):
        server = create_server()
        httpretty.enable()
        httpretty.register_uri(
            httpretty.POST,
            "http://skydocker.adtran.com/api/build",
            body='{"name": "foobar"}',
        )
        response = server.send_to_api(
            "post", "http://skydocker.adtran.com/api/build", {"name": "foobar"}
        )
        assert_that(response.status_code, is_(equal_to(200)))
        assert_that(response.json(), is_(equal_to({"name": "foobar"})))
        httpretty.disable()

    def test_patch_to_api_request(self):
        server = create_server()
        httpretty.enable()
        httpretty.register_uri(
            httpretty.PATCH,
            "http://skydocker.adtran.com/api/build",
            body='{"name": "foobar"}',
        )
        response = server.send_to_api(
            "patch", "http://skydocker.adtran.com/api/build", {"name": "foobar"}
        )
        assert_that(response.status_code, is_(equal_to(200)))
        assert_that(response.json(), is_(equal_to({"name": "foobar"})))
        httpretty.disable()
