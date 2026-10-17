"""Replace AVC groups; preserve source PMF headers, timing, and nonvideo packets."""
import re
import struct


def video_groups(payload):
    if payload[:4] != b'PSMF':
        raise ValueError('Missing PSMF header')
    offset, size = struct.unpack_from('>II', payload, 8)
    if offset + size != len(payload) or offset % 2048:
        raise ValueError('Unexpected PMF stream geometry')
    groups = []
    pos = offset
    while pos < len(payload):
        if payload[pos:pos + 3] != b'\0\0\1':
            raise ValueError('Invalid program stream boundary')
        code = payload[pos + 3]
        if code == 0xba:
            pos += 14 + (payload[pos + 13] & 7)
            continue
        if code == 0xb9:
            pos += 4
            continue
        length = 6 + int.from_bytes(payload[pos + 4:pos + 6], 'big')
        if pos + length > len(payload):
            raise ValueError('PES exceeds stream')
        if 0xe0 <= code <= 0xef:
            if code != 0xe0:
                raise ValueError('Multiple video streams unsupported')
            start = pos + 9 + payload[pos + 8]
            if payload[pos + 7] & 0x80:
                x = payload[pos + 9:pos + 14]
                pts = ((x[0] >> 1 & 7) << 30) | (x[1] << 22) | ((x[2] >> 1) << 15) | (x[3] << 7) | (x[4] >> 1)
                groups.append({'pts': pts, 'slots': []})
            if not groups:
                raise ValueError('Video begins without timestamp')
            groups[-1]['slots'].append((start, pos + length))
        pos += length
    if pos != len(payload):
        raise ValueError('PMF packet walk mismatch')
    return groups


def avc_access_units(stream):
    starts = [m.start() for m in re.finditer(b'\x00\x00\x00\x01\x09', stream)]
    if not starts or starts[0] != 0:
        raise ValueError('AVC must begin with four-byte AUD')
    return [stream[a:b] for a, b in zip(starts, starts[1:] + [len(stream)])]


def replace_video_groups(payload, stream, ticks_per_frame=3003):
    groups = video_groups(payload)
    units = avc_access_units(stream)
    first = groups[0]['pts']
    boundaries = []
    for group in groups:
        delta = group['pts'] - first
        if delta < 0 or delta % ticks_per_frame:
            raise ValueError('Non-integral frame timestamp')
        boundaries.append(delta // ticks_per_frame)
    if boundaries != sorted(set(boundaries)) or boundaries[-1] >= len(units):
        raise ValueError('Unexpected frame ordering')
    result = bytearray(payload)
    report = []
    for group, start, end in zip(groups, boundaries, boundaries[1:] + [len(units)]):
        data = b''.join(units[start:end])
        capacity = sum(b - a for a, b in group['slots'])
        if len(data) > capacity:
            raise ValueError('Group %d needs %d bytes; available %d' % (start, len(data), capacity))
        gap = capacity - len(data)
        filler = b'\0\0\0\1\x0c' + b'\xff' * (gap - 6) + b'\x80' if gap >= 6 else b'\0' * gap
        padded = data + filler
        cursor = 0
        for a, b in group['slots']:
            result[a:b] = padded[cursor:cursor + b - a]
            cursor += b - a
        report.append({'first_frame': start, 'last_frame_exclusive': end, 'avc_bytes': len(data), 'capacity': capacity})
    if len(result) != len(payload):
        raise ValueError('PMF size changed')
    return bytes(result), report
