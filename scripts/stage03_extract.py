"""Stage03 extract: copy ONLY eng_us.loc from ISO (read-only) to working copy."""
import os, struct
ISO = next(f for f in os.listdir(".") if f.lower().endswith(".iso"))
SECTOR = 2048
TARGET = "/PSP_GAME/USRDIR/data/locale/trc/eng_us.loc"

def parse_dir(fh, extent, size):
    fh.seek(extent * SECTOR)
    data = fh.read(size)
    recs = []
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
        rec = data[off:off+rl]
        ext = struct.unpack("<I", rec[2:6])[0]
        sz = struct.unpack("<I", rec[10:14])[0]
        flags = rec[25]
        nlen = rec[32]
        name_raw = rec[33:33+nlen]
        recs.append((name_raw, ext, sz, flags))
        off += rl
    return recs

def clean(b):
    if b == b"\x00": return "."
    if b == b"\x01": return ".."
    s = b.decode("utf-8", errors="replace")
    return s.split(";1")[0] if ";1" in s else s

with open(ISO, "rb") as fh:
    fh.seek(16 * SECTOR)
    pvd = fh.read(SECTOR)
    root_rec = pvd[156:190]
    root_ext = struct.unpack("<I", root_rec[2:6])[0]
    root_sz = struct.unpack("<I", root_rec[10:14])[0]
    queue = [("/", root_ext, root_sz)]
    seen = set()
    found = None
    while queue:
        path, ext, sz = queue.pop(0)
        if (ext, sz) in seen: continue
        seen.add((ext, sz))
        for name_raw, e, s, flags in parse_dir(fh, ext, sz):
            nm = clean(name_raw)
            if nm in (".", ".."): continue
            full = (path.rstrip("/") + "/" + nm) if path != "/" else ("/" + nm)
            if full.lower() == TARGET.lower():
                found = (e, s)
            if flags & 0x02:
                queue.append((full, e, s))
    assert found, "target not found"
    ext, sz = found
    print(f"target {TARGET} extent={ext} size={sz}")
    fh.seek(ext * SECTOR)
    data = fh.read(sz)
    assert len(data) == sz
    with open("logs/stage03/eng_us_orig.loc", "wb") as out:
        out.write(data)
    print(f"wrote logs/stage03/eng_us_orig.loc ({len(data)} bytes)")
