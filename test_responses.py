from __future__ import (
    absolute_import, print_function, division, unicode_literals
)

import requests
import responses
import pytest
import json

from requests.exceptions import ConnectionError


def assert_reset():
    assert len(responses._default_mock._urls) == 0
    assert len(responses.calls) == 0


def assert_response(resp, body=None, content_type='text/plain'):
    assert resp.status_code == 200
    assert resp.headers['Content-Type'] == content_type
    assert resp.text == body


def test_response():
    @responses.activate
    def run():
        responses.add(responses.GET, 'http://example.com', body=b'test')
        resp = requests.get('http://example.com')
        assert_response(resp, 'test')
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == 'http://example.com/'
        assert responses.calls[0].response.content == b'test'

    run()
    assert_reset()


def test_connection_error():
    @responses.activate
    def run():
        responses.add(responses.GET, 'http://example.com')

        with pytest.raises(ConnectionError):
            requests.get('http://example.com/foo')

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == 'http://example.com/foo'
        assert type(responses.calls[0].response) is ConnectionError

    run()
    assert_reset()


def test_match_querystring():
    @responses.activate
    def run():
        url = 'http://example.com?test=1&foo=bar'
        responses.add(
            responses.GET, url,
            match_querystring=True, body=b'test')
        resp = requests.get('http://example.com?test=1&foo=bar')
        assert_response(resp, 'test')
        resp = requests.get('http://example.com?foo=bar&test=1')
        assert_response(resp, 'test')

    run()
    assert_reset()


def test_match_querystring_error():
    @responses.activate
    def run():
        responses.add(
            responses.GET, 'http://example.com/?test=1',
            match_querystring=True)

        with pytest.raises(ConnectionError):
            requests.get('http://example.com/foo/?test=2')

    run()
    assert_reset()


def test_accept_string_body():
    @responses.activate
    def run():
        url = 'http://example.com/'
        responses.add(
            responses.GET, url, body='test')
        resp = requests.get(url)
        assert_response(resp, 'test')

    run()
    assert_reset()


def test_add_json():
    @responses.activate
    def run():
        url = 'http://example.com/'
        body = {'some-key': 'a-value'}
        responses.add_json(responses.GET, url, body=body)
        resp = requests.get(url)
        assert_response(resp, json.dumps(body),
                        content_type='application/json')

    run()
    assert_reset()
