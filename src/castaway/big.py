"""Validated BIGF directory reader, preserving payloads verbatim."""
import struct

def read_big(data):
    if data[:4] not in (b'BIGF', b'BIG4') or len(data) < 16:
        raise ValueError('Not a supported BIG archive')
    count, directory_end = struct.unpack_from('>II', data, 8)
    if count > 100000 or not 16 <= directory_end <= len(data):
        raise ValueError('Invalid BIG directory bounds')
    pos, entries = 16, []
    for _ in range(count):
        offset, size = struct.unpack_from('>II', data, pos)
        end = data.index(0, pos+8, directory_end)
        name = data[pos+8:end].decode('ascii')
        if offset < directory_end or offset+size > len(data):
            raise ValueError('Invalid BIG payload bounds')
        entries.append((name, offset, data[offset:offset+size]))
        pos = end+1
    return entries
