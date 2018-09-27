# -*- coding: utf-8 -*-

import base64
from Crypto.Cipher import AES

IV = 16 * '\x00'
cipher = AES.new('1234567890123456', AES.MODE_ECB, IV=IV)

def encode_string(string):
    return base64.b64encode(cipher.encrypt(string.rjust(32)))

def decode_string(string):
    return cipher.decrypt(base64.b64decode(string)).strip()