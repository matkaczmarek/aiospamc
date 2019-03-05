#!/usr/bin/env python3
#pylint: disable=no-self-use

import zlib

import pytest

from aiospamc.headers import Compress, ContentLength, XHeader
from aiospamc.requests import Request


def test_request_instantiates():
    request = Request('TEST')

    assert 'request' in locals()


def test_request_to_bytes_method():
    method = 'TEST'
    expected = b'TEST SPAMC/1.5\r\n\r\n'

    r = Request(method)

    assert expected == bytes(r)


@pytest.mark.parametrize('headers,expected', [
    (None, b'TEST SPAMC/1.5\r\n\r\n'),
    ({'X-Header': 'value'}, b'TEST SPAMC/1.5\r\nX-Header: value\r\n\r\n'),
    ({'X-Header': XHeader(name='X-Header', value='value')}, b'TEST SPAMC/1.5\r\nX-Header: value\r\n\r\n'),
    ({'X-Header': 'value', 'X-Header2': 'value2'}, b'TEST SPAMC/1.5\r\nX-Header: value\r\nX-Header2: value2\r\n\r\n'),
])
def test_request_to_bytes_headers(headers, expected):
    r = Request(method='TEST', headers=headers)

    assert expected == bytes(r)


@pytest.mark.parametrize('body,expected', [
    (None, b'TEST SPAMC/1.5\r\n\r\n'),
    (b'Test body', b'TEST SPAMC/1.5\r\n\r\nTest body'),
    ('Test body', b'TEST SPAMC/1.5\r\n\r\nTest body'),
])
def test_request_to_bytes_body(body, expected):
    r = Request(method='TEST', body=body)

    assert expected == bytes(r)

# @pytest.mark.parametrize('method,headers,body,compress,user,message_class,set_,remove', [
#     ('TEST', None, {}),
#     ('TEST', None, {'X-Tests-Head': 'Tests value'}),
#     ('TEST', None, {'X-Tests-Head': XHeader('X-Tests-Head', 'Tests value')}),
#     ('TEST', 'Test body\n', None),
#     ('TEST', 'Test body\n', [ContentLength(length=10), Compress()])
# ])
# def test_request_bytes(method, body, headers):
#     request = Request(method=method, body=body, headers=headers)
#
#     assert bytes(request).startswith(method.encode())
#     assert bytes(b'SPAMC/1.5\r\n') in bytes(request)
#     assert all(bytes(header) in bytes(request) for header in headers)
#     if body:
#         if any(isinstance(header, Compress) for header in headers):
#             assert bytes(request).endswith(zlib.compress(body.encode()))
#         else:
#             assert bytes(request).endswith(body.encode())
