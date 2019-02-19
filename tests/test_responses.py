#!/usr/bin/env python3

import zlib

import pytest

from aiospamc.headers import Compress
from aiospamc.responses import Response
from aiospamc.status import Status


def test_response_instantiates():
    response = Response('1.5', Status.EX_OK, 'EX_OK')

    assert 'response' in locals()


@pytest.mark.parametrize('version,status,message,body,headers', [
    ('1.5', Status.EX_OK, 'EX_OK', None, []),
    ('1.5', Status.EX_OK, 'EX_OK', 'Test body\n', []),
    ('1.5', Status.EX_OK, 'EX_OK', 'Test body\n', [Compress()]),
])
def test_response_bytes(version, status, message, body, headers):
    response = Response(version=version,
                        status_code=status,
                        message=message,
                        body=body,
                        headers=headers)

    assert bytes(response).startswith(b'SPAMD/%b' % version.encode())
    assert b' %d ' % status.value in bytes(response)
    assert b' %b\r\n' % message.encode() in bytes(response)
    assert all(bytes(header) in bytes(response) for header in headers)
    if body:
        if any(isinstance(header, Compress) for header in headers):
            assert bytes(response).endswith(zlib.compress(body.encode()))
        else:
            assert bytes(response).endswith(body.encode())
