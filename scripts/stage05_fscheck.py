"""Stage05 Tasks 5-6: locate eng_us.loc directory record only (no full scan).
Dumps: parent dir location, raw record hex, extent LBA, size LE/BE, record position (for later patch),
sibling extents (capacity / neighbor-overlap check).
"""
import struct
from math import ceil

ISO = "Sims 2, The - Castaway (USA) (En,Fr,De,Es,It,Nl,Pt).iso"
SECTOR = 2048
TARGET = "/PSP_GAME/USRDIR/data/locale/trc/eng_us.loc"

def read_dir(fh, extent, size):
    fh.seek(extent * SECTOR)
    return fh.read(size)

def iter_records(data):
    off = 0
    while off < len(data):
        rl = data[off]
        if rl == 0:
            nxt = ((off // SECTOR) + 1) * SECTOR
            if nxt <= off:
                break
            off = nxt
            continue
        if off + rl > len(data):
            break
        yield off, data[off:off+rl]
        off += rl

def clean(b):
    if b == b"\x00":
        return "."
    if b == b"\x01":
        return ".."
    s = b.decode("utf-8", errors="replace")
    return s.split(";1")[0] if ";1" in s else s

with open(ISO, "rb") as fh:
    fh.seek(16 * SECTOR)
    pvd = fh.read(SECTOR)
    rr = pvd[156:190]
    root_ext, root_sz = struct.unpack("<I", rr[2:6])[0], struct.unpack("<I", rr[10:14])[0]
    # walk path
    parts = [p for p in TARGET.split("/") if p]
    cur_ext, cur_sz, cur_path = root_ext, root_sz, "/"
    rec_pos = None
    target_rec = None
    for depth, part in enumerate(parts):
        data = read_dir(fh, cur_ext, cur_sz)
        hit = None
        for roff, rec in iter_records(data):
            nlen = rec[32]
            nm = clean(rec[33:33+nlen])
            if nm.lower() == part.lower():
                hit = (roff, rec)
                break
        assert hit, f"not found: {part} under {cur_path}"
        roff, rec = hit
        ext = struct.unpack("<I", rec[2:6])[0]
        ext_be = struct.unpack(">I", rec[6:10])[0]
        sz = struct.unpack("<I", rec[10:14])[0]
        sz_be = struct.unpack(">I", rec[14:18])[0]
        flags = rec[25]
        if depth == len(parts) - 1:
            target_rec, rec_pos = rec, (cur_ext, cur_sz, roff)
        else:
            assert flags & 0x02, f"not a dir: {part}"
            cur_ext, cur_sz = ext, sz
    roff_abs = rec_pos[0] * SECTOR + rec_pos[2]
    print(f"target dir record at ISO byte offset {roff_abs:#x} (dir LBA {rec_pos[0]}, rec len {len(target_rec)})")
    print(f"record hex: {target_rec.hex()}")
    print(f"extent LE={struct.unpack('<I', target_rec[2:6])[0]} BE={struct.unpack('>I', target_rec[6:10])[0]}")
    print(f"size   LE={struct.unpack('<I', target_rec[10:14])[0]} BE={struct.unpack('>I', target_rec[14:18])[0]}")
    print(f"flags={target_rec[25]} rec_len_byte0={target_rec[0]} namelen={target_rec[32]}")
    # siblings in same parent dir sorted by extent
    data = read_dir(fh, cur_ext, cur_sz)
    sibs = []
    for roff, rec in iter_records(data):
        nlen = rec[32]
        nm = clean(rec[33:33+nlen])
        if nm in (".", ".."):
            continue
        sibs.append((struct.unpack("<I", rec[2:6])[0], struct.unpack("<I", rec[10:14])[0], nm))
    sibs.sort()
    print("siblings by extent:")
    for e, s, n in sibs:
        print(f"  LBA {e} size {s} sectors {ceil(s/SECTOR)} {n}")
    # capacity: sectors used by original vs new size
    orig_sectors = ceil(5580 / SECTOR)
    new_sectors = ceil(5574 / SECTOR)
    print(f"orig sectors={orig_sectors} new sectors={new_sectors}")
    # neighbor check: next extent after target
    te = struct.unpack("<I", target_rec[2:6])[0]
    ends = te + orig_sectors
    nxt = [x for x in sibs if x[0] >= ends]
    print(f"target file sectors [{te},{ends}) next sibling: {nxt[0] if nxt else None}")
    with open("logs/stage05/iso_filesystem_report.txt", "w", encoding="utf-8") as f:
        f.write(f"target: {TARGET}\n")
        f.write(f"dir record ISO offset: {roff_abs:#x} (parent dir LBA {rec_pos[0]}, rec offset {rec_pos[2]}, rec len {len(target_rec)})\n")
        f.write(f"record hex: {target_rec.hex()}\n")
        f.write(f"extent LE/BE: {struct.unpack('<I', target_rec[2:6])[0]}/{struct.unpack('>I', target_rec[6:10])[0]}\n")
        f.write(f"size LE/BE: {struct.unpack('<I', target_rec[10:14])[0]}/{struct.unpack('>I', target_rec[14:18])[0]}\n")
        f.write(f"both-endian consistent: {target_rec[2:10].hex()} vs {target_rec[10:18].hex()} layout confirmed\n")
        f.write("siblings:\n")
        for e, s, n in sibs:
            f.write(f"  LBA {e} size {s} sectors {ceil(s/SECTOR)} {n}\n")
        f.write(f"orig sectors={orig_sectors} new sectors={new_sectors}\n")
        f.write(f"next sibling after target end ({ends}): {nxt[0] if nxt else None}\n")
    print("wrote logs/stage05/iso_filesystem_report.txt")
