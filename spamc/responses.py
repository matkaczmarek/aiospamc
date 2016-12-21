#!/usr/bin/env python3

import enum
import re

from spamc.headers import header_from_string


class SpamdStatus(enum.IntEnum):
    def __new__(cls, value, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        
        return obj
    
    EX_OK           = 0,  'No problems'
    EX_USAGE        = 64, 'Command line usage error'
    EX_DATAERR      = 65, 'Data format error'
    EX_NOINPUT      = 66, 'Cannot open input'
    EX_NOUSER       = 67, 'Addressee unknown'
    EX_NOHOST       = 68, 'Host name unknown'
    EX_UNAVAILABLE  = 69, 'Service unavailable'
    EX_SOFTWARE     = 70, 'Internal software error'
    EX_OSERR        = 71, 'System error (e.g., can\'t fork)'
    EX_OSFILE       = 72, 'Critical OS file missing'
    EX_CANTCREAT    = 73, 'Can\'t create (user) output file'
    EX_IOERR        = 74, 'Input/output error'
    EX_TEMPFAIL     = 75, 'Temp failure; user is invited to retry'
    EX_PROTOCOL     = 76, 'Remote error in protocol'
    EX_NOPERM       = 77, 'Permission denied'
    EX_CONFIG       = 78, 'Configuration error'
    EX_TIMEOUT      = 79, 'Read timeout'


class SpamdResponse:
    headers_pattern = re.compile(r'^\s*(?P<protocol>SPAMD)/(?P<version>\d+\.\d+)\s+(?P<status>\d+)\s+(?P<message>.*\r\n)(?P<headers>(.*:.*\r\n)*)')
    
    @classmethod
    def parse(cls, response):
        header, *body = response.split('\r\n\r\n', 1)
        
        # Process headers
        match = cls.headers_pattern.match(header)
        if match:
            header_match = match.groupdict()
        else:
            # Not a SPAMD response
            return None
        
        protocol_version = header_match['version'].strip()
        status_code = SpamdStatus(int(header_match['status']))
        message = header_match['message'].strip()
        header_list = []
        for h in header_match['headers'].split('\r\n'):
            if h == '':
                continue
            header_obj = header_from_string(h)
            if header_obj:
                header_list.append(header_obj)
        
        if body != []:
            obj = cls(protocol_version, status_code, message, header_list, body[0])
        else:
            obj = cls(protocol_version, status_code, message, header_list)
            
        return obj
    
    def __repr__(self):
        return 'SpamdResponse(protocol_version={}, status_code={}, message={}, headers={}, body={})'.format(self.protocol_version, self.status_code, self.message, self.headers, self.body)
    
    def __str__(self):
        return 'SpamdResponse [Status Code: {}, Message: ]'.format(self.status_code, self.message)
    
    def __init__(self, protocol_version, status_code, message, headers = [], body = None):
        self.protocol_version = protocol_version
        self.status_code = status_code
        self.message = message
        self.headers = headers
        self.body = body