#!/usr/bin/env python3

'''Contains all requests that can be made to the SPAMD service.'''

import zlib
from email.message import EmailMessage
from email import message_from_string

from .common import request_to_bytes
from .headers import Compress, Header, MessageClass, Remove, Set, User
from .options import ActionOption, MessageClassOption
from .parser import Parser


class Request:
    '''SPAMC request object.

    Attributes
    ----------
    method : :obj:`str`
        Method name of the request.
    version : :obj:`str`
        Protocol version.
    body : :obj:`str` or :obj:`bytes`
        String representation of the body.  An instance of the
        :class:`aiospamc.headers.ContentLength` will be automatically added.
    TODO: document attributes
    '''

    def __init__(self, method, headers=None, body=None, compress=None,
                 user=None, message_class=None, set_=None, remove=None):
        '''Request constructor.

        Parameters
        ----------
        method : :obj:`str`
            Method name of the request.
        body : :obj:`str` or :obj:`bytes`, optional
            String representation of the body.  An instance of the
            :class:`aiospamc.headers.ContentLength` will be automatically added.
        headers : tuple of :class:`aiospamc.headers.Header`, optional
            Collection of headers to be added.  If it contains an instance of
            :class:`aiospamc.headers.Compress` then the body is automatically
            compressed.
        TODO: finish and update docstring
        '''

        self.method = method
        self.headers = headers if headers is not None else dict()
        self.body = body
        self.compress = compress
        self.user = user
        self.message_class = message_class
        self.set_ = set_
        self.remove = remove

    @classmethod
    def from_parser(cls, method, _, headers, body):
        compress = False
        message_class = None
        set_ = None
        remove = None
        user = None

        headers_dict = {header.field_name(): header for header in headers}
        if 'Compress' in headers_dict:
            body = zlib.decompress(body)
            compress = True
        if 'Message-class' in headers_dict:
            message_class = headers_dict['Message-class'].value
        if 'Set' in headers_dict:
            set_ = headers_dict['Set'].action
        if 'Remove' in headers_dict:
            remove = headers_dict['Remove'].action
        if 'User' in headers_dict:
            user = headers_dict['User'].name

        return cls(
            method=method,
            headers=headers_dict,
            body=body,
            compress=compress,
            user=user,
            message_class=message_class,
            set_=set_,
            remove=remove
        )

    @classmethod
    def from_raw_request(cls, request):
        return cls(method=request.method, headers=request.headers, )

    def _prepare_body(self):
        '''Convert the body to a :obj:`bytes` object.'''

        if not self.body:
            return b''
        elif type(self.body) == bytes:
            return self.body
        elif type(self.body) == str:
            return message_from_string(self.body).as_bytes()
        elif type(self.body) == EmailMessage:
            return self.body.as_bytes()
        else:
            try:
                return bytes(self.body)
            except TypeError:
                raise TypeError('Unsupported type in body', self, self.body)

    def _prepare_headers(self):
        headers = {}

        for name, value in self.headers.items():
            if issubclass(type(value), Header):
                headers[name] = value
            elif type(value) == str:
                parser = Parser('{}:{}\r\n'.format(name, value).encode())
                headers[name] = parser.header()

        if type(self.message_class) == str:
            parser = Parser(self.message_class)
            self.headers['Message-class'] = parser.message_class_value()
        elif type(self.message_class) == MessageClassOption:
            self.headers['Message-class'] = self.message_class

        if type(self.remove) == str:
            parser = Parser(self.remove)
            self.headers['Remove'] = parser.set_remove_value()
        elif type(self.remove) == ActionOption:
            self.headers['Remove'] = self.remove

        if type(self.set_) == str:
            parser = Parser(self.set_)
            self.headers['Set'] = parser.set_remove_value()
        elif type(self.set_) == ActionOption:
            self.headers['Set'] = self.set_

        if type(self.user) == str:
            parser = Parser(self.user.encode())
            self.headers['User'] = parser.user_value()
        elif type(self.user) == ActionOption:
            self.headers['User'] = self.user

        return headers.values()

    def prepare(self):
        body = self._prepare_body()
        headers = self._prepare_headers()

        if self.compress or Compress in [type(header) for header in headers]:
            body = zlib.compress(body)

        return request_to_bytes(self.method, headers, body)

    def __bytes__(self):
        return self.prepare()



# class OldRequest(RequestResponseBase):
#     '''SPAMC request object.
#
#     Attributes
#     ----------
#     verb : :obj:`str`
#         Method name of the request.
#     version : :obj:`str`
#         Protocol version.
#     body : :obj:`str` or :obj:`bytes`
#         String representation of the body.  An instance of the
#         :class:`aiospamc.headers.ContentLength` will be automatically added.
#     '''
#
#     def __init__(self, verb, version='1.5', headers=None, body=None):
#         '''Request constructor.
#
#         Parameters
#         ----------
#         verb : :obj:`str`
#             Method name of the request.
#         version: :obj:`str`
#             Version of the protocol.
#         body : :obj:`str` or :obj:`bytes`, optional
#             String representation of the body.  An instance of the
#             :class:`aiospamc.headers.ContentLength` will be automatically added.
#         headers : tuple of :class:`aiospamc.headers.Header`, optional
#             Collection of headers to be added.  If it contains an instance of
#             :class:`aiospamc.headers.Compress` then the body is automatically
#             compressed.
#         '''
#
#         self.verb = verb
#         self.version = version
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
#         request = (b'%(verb)b '
#                    b'SPAMC/%(version)b'
#                    b'\r\n'
#                    b'%(headers)b\r\n'
#                    b'%(body)b')
#
#         return request % {b'verb': self.verb.encode(),
#                           b'version': self.version.encode(),
#                           b'headers': b''.join(map(bytes, self._headers.values())),
#                           b'body': body}
