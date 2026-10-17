"""Read-only ISO9660 metadata and file access (no third-party dependencies)."""
import struct

class Iso9660:
    def __init__(self, path):
        self.path = path
        self.files = {}
        with open(path, 'rb') as f:
            f.seek(16 * 2048)
            pvd = f.read(2048)
            if pvd[:7] != b'\x01CD001\x01':
                raise ValueError('Unsupported ISO9660 primary volume')
            self.volume = pvd[40:72].decode('ascii').strip()
            root = pvd[156:190]
            self._walk(f, struct.unpack_from('<I', root, 2)[0], struct.unpack_from('<I', root, 10)[0], '')

    def _walk(self, f, extent, size, parent):
        f.seek(extent * 2048)
        data = f.read(size)
        if len(data) != size:
            raise ValueError('Truncated directory')
        pos = 0
        children = []
        while pos < size:
            length = data[pos]
            if not length:
                pos = (pos // 2048 + 1) * 2048
                continue
            rec = data[pos:pos+length]
            if length < 34 or len(rec) != length:
                raise ValueError('Invalid directory record')
            name = rec[33:33+rec[32]]
            pos += length
            if name in (b'\x00', b'\x01'):
                continue
            name = name.decode('ascii').split(';')[0]
            path = parent + '/' + name
            ex, sz = struct.unpack_from('<I', rec, 2)[0], struct.unpack_from('<I', rec, 10)[0]
            if rec[25] & 2:
                children.append((ex, sz, path))
            else:
                self.files[path] = {'extent': ex, 'size': sz, 'record_offset': extent*2048+pos-length}
        for child in children:
            self._walk(f, *child)

    def read(self, path):
        entry = self.files[path]
        with open(self.path, 'rb') as f:
            f.seek(entry['extent'] * 2048)
            data = f.read(entry['size'])
        if len(data) != entry['size']:
            raise ValueError('Truncated file: ' + path)
        return data

def parse_sfo(data):
    if data[:4] != b'\x00PSF':
        raise ValueError('Invalid SFO')
    _, _, keys, values, count = struct.unpack_from('<5I', data)
    result = {}
    for i in range(count):
        keyoff, fmt, size, capacity, valueoff = struct.unpack_from('<HHIII', data, 20+i*16)
        start = keys+keyoff
        key = data[start:data.index(0, start)].decode('utf-8')
        value = data[values+valueoff:values+valueoff+size]
        result[key] = struct.unpack('<I', value)[0] if fmt == 0x404 else value.rstrip(b'\x00').decode('utf-8', 'replace')
    return result

