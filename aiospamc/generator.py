#!/usr/bin/env python3

from email.generator import Generator


class CharsetGenerator(Generator):
    def __init__(self, outfp, mangle_from_=None, maxheaderlen=None, *, policy=None):
        self.charset_stack = list()
        self._fp = outfp

    # for part in message.walk()
    #   charset = part.get_content_charset()
    #   return part.get_payload(charset)

    def write(self, b):
        self._fp.write(b)

    def encode(self, s):
        self.write(s.encode(self.charset_stack[-1]))

    def flatten(self, msg, unixfrom=False, linesep=None):
        self.handle_headers(msg)
        main = msg.get_content_maintype()
        if main == 'text':
            self.handle_text(msg)

    def handle_headers(self, msg):
        charset = msg.get_charset() or 'ascii'
        self.charset_stack.append(charset)
        for name, value in msg.items():
            self.encode(':'.join([name, value]) + '\n')
        self.encode('\n')
        self.charset_stack.pop()

    def handle_text(self, msg):
        charset = msg.get_content_charset() or 'ascii'
        self.charset_stack.append(charset)
        self.encode(msg.get_payload())
        self.charset_stack.pop()
