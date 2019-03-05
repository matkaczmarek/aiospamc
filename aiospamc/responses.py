#!/usr/bin/env python3

'''Contains classes used for responses.'''

from email import message_from_bytes

from .common import response_to_bytes


class Response:
    '''TODO: attribute documentation'''

    def __init__(self, status_code, message, headers=None, body=None, request=None):
        '''TODO: init documentation'''

        self.status_code = status_code
        self.message = message
        self.headers = headers
        self.body = body
        self.request = request

    @classmethod
    def from_parser(cls, _, status_code, message, headers, body):
        headers = {header.field_name(): header for header in headers}
        return cls(status_code, message, headers, body)

    def body_as_email_message(self):
        return message_from_bytes(self.body)

    def raise_for_exception(self):
        raise self.status_code.value[1](
            response=self,
            message=self.status_code.value[2]
        )

    def __bytes__(self):
        return response_to_bytes(self.status_code, self.message, self.headers.values(), self.body)


# class Response(RequestResponseBase):
#     '''Class to encapsulate response.
#
#     Attributes
#     ----------
#     protocol_version : :obj:`str`
#         Protocol version given by the response.
#     status_code : :class:`aiospamc.responess.Status`
#         Status code give by the response.
#     message : :obj:`str`
#         Message accompanying the status code.
#     body : :obj:`str` or :obj:`bytes`
#         Contents of the response body.
#     '''
#
#     def __init__(self, version, status_code, message, headers=None, body=None):
#         '''Response constructor.
#
#         Parameters
#         ----------
#         version : :obj:`str`
#             Version reported by the SPAMD service response.
#         status_code : :class:`aiospamc.responses.Status`
#             Success or error code.
#         message : :obj:`str`
#             Message associated with status code.
#         body : :obj:`str` or :obj:`bytes`, optional
#             String representation of the body.  An instance of the
#             :class:`aiospamc.headers.ContentLength` will be automatically added.
#         headers : tuple of :class:`aiospamc.headers.Header`, optional
#             Collection of headers to be added.  If it contains an instance of
#             :class:`aiospamc.headers.Compress` then the body is automatically
#             compressed.
#         '''
#
#         self.version = version
#         self.status_code = status_code
#         self.message = message
#         super().__init__(body, headers)
#
#     def __bytes__(self):
#         if self._compressed_body:
#             body = self._compressed_body
#         elif self.body:
#             body = self.body.encode()
#         else:
#             body = b''
#
#         return (b'SPAMD/%(version)b '
#                 b'%(status)d '
#                 b'%(message)b\r\n'
#                 b'%(headers)b\r\n'
#                 b'%(body)b') % {b'version': b'1.5',
#                                 b'status': self.status_code.value,
#                                 b'message': self.message.encode(),
#                                 b'headers': b''.join(map(bytes, self._headers.values())),
#                                 b'body': body}
