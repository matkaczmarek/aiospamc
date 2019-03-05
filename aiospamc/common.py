#!/usr/bin/env python3

'''Common classes for the project.'''


REQUEST_1_5 = (b'%(method)b '
               b'SPAMC/%(version)b'
               b'\r\n'
               b'%(headers)b\r\n'
               b'%(body)b')

RESPONSE_1_5 = (b'SPAMD/%(version)b '
                b'%(status)d '
                b'%(message)b\r\n'
                b'%(headers)b\r\n'
                b'%(body)b')


def request_to_bytes(method, headers, body):
    return REQUEST_1_5 % {
        b'method': method.encode(),
        b'version': b'1.5',
        b'headers': b''.join(map(bytes, headers)),
        b'body': body
    }


def response_to_bytes(status_code, message, headers, body):
    return RESPONSE_1_5 % {
        b'version': b'1.5',
        b'status': status_code.value,
        b'message': message.encode(),
        b'headers': b''.join(map(bytes, headers.values())),
        b'body': body
    }


class RawRequest:
    def __init__(self, method, version, headers, body):
        self.method = method
        self.version = version
        self.headers = headers
        self.body = body

    def __bytes__(self):
        return request_to_bytes(
            self.method,
            self.headers,
            self.body
        )


class RawResponse:
    def __init__(self, version, status_code, message, headers, body):
        self.version = version
        self.status_code = status_code
        self.message = message
        self.headers = headers
        self.body = body

    def __bytes__(self):
        return response_to_bytes(
            self.version,
            self.status_code,
            self.message,
            self.headers,
            self.body
        )

# import zlib
#
# from .headers import ContentLength
#
#
# class RequestResponseBase:
#     '''Base class for requests and responses.'''
#
#     def __init__(self, body=None, headers=None):
#         '''
#         Parameters
#         ----------
#         body : :obj:`str`, optional
#             String representation of the body.  An instance of the
#             aiospamc.headers.ContentLength will be automatically added.
#         headers : tuple of :class:`aiospamc.headers.Header`, optional
#             Collection of headers to be added.  If it contains an instance of
#             aiospamc.headers.Compress then the body is automatically
#             compressed.
#         '''
#
#         if headers:
#             self._headers = {item.field_name(): item for item in headers}
#         else:
#             self._headers = {}
#         self._body = ''
#         self._compressed_body = None
#         if body:
#             if isinstance(body, str):
#                 self.body = body
#             elif isinstance(body, bytes):
#                 self.body = self._decode_body(body, self._headers.values())
#
#     @staticmethod
#     def _decode_body(body, headers):
#         '''Parses a body of a response.
#
#         Parameters
#         ----------
#         body : bytes
#             Bytes representation of body.
#         headers : :obj:`tuple` or :obj:`list` of :class:`aiospamc.headers.Header`
#             Collection of headers.
#
#         Returns
#         -------
#         str
#             Body in a string object.
#         '''
#
#         if not body:
#             return None
#         elif any(header.field_name() == 'Compress' for header in headers):
#             return zlib.decompress(body).decode()
#         else:
#             return body.decode()
#
#     @property
#     def body(self):
#         '''Contains the contents of the body.
#
#         The getter will return a bytes object.
#
#         The setter expects a string.  If the :class:`aiospamc.headers.Compress`
#         header is present then the value of body will be compressed.
#
#         The deleter will automatically remove the
#         :class:`aiospamc.headers.ContentLength` header.
#         '''
#
#         return self._body
#
#     @body.setter
#     def body(self, value):
#         self._body = value
#         if 'Compress' in self._headers:
#             self._compress_body()
#         self._set_content_length(value)
#
#     @body.deleter
#     def body(self):
#         self._body = ''
#         self._compressed_body = None
#         self.delete_header('Content-length')
#
#     def _compress_body(self):
#         self._compressed_body = zlib.compress(self.body.encode())
#         self._set_content_length(self._compressed_body)
#
#     def _decompress_body(self):
#         self._compressed_body = None
#         self._set_content_length(self.body)
#
#     def _set_content_length(self, body_):
#         self.add_header(ContentLength(len(body_)))
#
#     def add_header(self, header):
#         '''Adds a header to the request.  A header with the same name will be
#         overwritten.
#
#         Parameters
#         ----------
#         header : :class:`aiospamc.headers.Header`
#             A header object to be added.
#         '''
#
#         if header.field_name() == 'Compress' and self.body:
#             self._compress_body()
#         self._headers[header.field_name()] = header
#
#     def get_header(self, header_name):
#         '''Gets the header matching the name.
#
#         Parameters
#         ----------
#         header_name : :obj:`str`
#             String name of the header.
#
#         Returns
#         -------
#         :class:`aiospamc.headers.Header`
#             A Header object or subclass of it.
#
#         Raises
#         ------
#         :class:`KeyError`
#         '''
#
#         return self._headers[header_name]
#
#     def delete_header(self, header_name):
#         '''Deletes the header from the request.
#
#         Parameters
#         ----------
#         header_name : :obj:`str`
#             String name of the header.
#
#         Raises
#         ------
#         :class:`KeyError`
#         '''
#
#         if header_name == 'Compress' and self.body:
#             self._decompress_body()
#         self._headers.pop(header_name)
