#!/usr/bin/env python3

'''Contains classes used for responses.'''

from .common import RequestResponseBase


class Response(RequestResponseBase):
    '''Class to encapsulate response.

    Attributes
    ----------
    protocol_version : :obj:`str`
        Protocol version given by the response.
    status_code : :class:`aiospamc.responess.Status`
        Status code give by the response.
    message : :obj:`str`
        Message accompanying the status code.
    body : :obj:`str` or :obj:`bytes`
        Contents of the response body.
    '''

    def __init__(self, version, status_code, message, headers=None, body=None):
        '''Response constructor.

        Parameters
        ----------
        version : :obj:`str`
            Version reported by the SPAMD service response.
        status_code : :class:`aiospamc.responses.Status`
            Success or error code.
        message : :obj:`str`
            Message associated with status code.
        body : :obj:`str` or :obj:`bytes`, optional
            String representation of the body.  An instance of the
            :class:`aiospamc.headers.ContentLength` will be automatically added.
        headers : tuple of :class:`aiospamc.headers.Header`, optional
            Collection of headers to be added.  If it contains an instance of
            :class:`aiospamc.headers.Compress` then the body is automatically
            compressed.
        '''

        self.version = version
        self.status_code = status_code
        self.message = message
        super().__init__(body, headers)

    def __bytes__(self):
        if self._compressed_body:
            body = self._compressed_body
        elif self.body:
            body = self.body.encode()
        else:
            body = b''

        return (b'SPAMD/%(version)b '
                b'%(status)d '
                b'%(message)b\r\n'
                b'%(headers)b\r\n'
                b'%(body)b') % {b'version': b'1.5',
                                b'status': self.status_code.value,
                                b'message': self.message.encode(),
                                b'headers': b''.join(map(bytes, self._headers.values())),
                                b'body': body}
