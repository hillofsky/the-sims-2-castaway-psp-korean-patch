"""LOCH/LOCL UTF-16 tables used by PSP save/load dialogs."""
import struct

def parse_locale(payload):
    if payload[:4] != b'LOCH':
        raise ValueError('Missing LOCH header')
    base = struct.unpack_from('<I', payload, 16)[0]
    if payload[base:base + 4] != b'LOCL':
        raise ValueError('Missing LOCL header')
    length, unknown, count = struct.unpack_from('<III', payload, base + 4)
    if base + length != len(payload):
        raise ValueError('Locale length mismatch')
    pointers = struct.unpack_from('<%dI' % count, payload, base + 16)
    result = []
    for pointer in pointers:
        if pointer < 16 + count * 4 or pointer >= length or pointer % 2:
            raise ValueError('Invalid locale string pointer')
        start = end = base + pointer
        while end + 2 <= len(payload) and payload[end:end + 2] != b'\0\0':
            end += 2
        if end + 2 > len(payload):
            raise ValueError('Unterminated locale string')
        result.append(payload[start:end].decode('utf-16le'))
    return base, pointers, result

def rebuild_locale(payload, strings):
    base, pointers, original = parse_locale(payload)
    if len(strings) != len(original):
        raise ValueError('Locale string count changed')
    result = bytearray(payload[:base + pointers[0]])
    for i, value in enumerate(strings):
        if '\0' in value:
            raise ValueError('Embedded NUL in locale string')
        struct.pack_into('<I', result, base + 16 + i * 4, len(result) - base)
        result.extend(value.encode('utf-16le') + b'\0\0')
    result.extend(b'\0' * (-len(result) % 4))
    struct.pack_into('<I', result, base + 4, len(result) - base)
    if parse_locale(bytes(result))[2] != list(strings):
        raise ValueError('Locale rebuild mismatch')
    return bytes(result)
