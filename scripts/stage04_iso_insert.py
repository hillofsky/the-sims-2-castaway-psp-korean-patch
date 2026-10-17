"""Stage04 ISO copy + single-file insert (same-size in-place).
- Copies original ISO to test ISO (no overwrite of original).
- Looks up eng_us.loc extent/size via ISO9660 TOC (no hardcoded LBA in logic; prints it for log).
- Overwrites ONLY those 5580 bytes in the copy.
- Verifies by re-read and full chunked ISO diff (expect exactly 6 differing bytes).
Usage: python stage04_iso_insert.py
"""
import os, struct, hashlib, shutil

WORKDIR = os.path.dirname(os.path.abspath(__file__)) if False else "."
ORIG = "Sims 2, The - Castaway (USA) (En,Fr,De,Es,It,Nl,Pt).iso"
TEST = "The_Sims_2_STAGE04_TEST.iso"
TARGET = "/PSP_GAME/USRDIR/data/locale/trc/eng_us.loc"
MOD = "logs/stage04/eng_us_test.loc"
SECTOR = 2048

def parse_dir(fh, extent, size):
    fh.seek(extent * SECTOR)
    data = fh.read(size)
    recs, off = [], 0
    while off < len(data):
        rl = data[off]
        if rl == 0:
            nxt = ((off // SECTOR) + 1) * SECTOR
            if nxt <= off: break
            off = nxt
            continue
        if off + rl > len(data): break
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

def find_target(iso):
    with open(iso, "rb") as fh:
        fh.seek(16 * SECTOR)
        pvd = fh.read(SECTOR)
        rr = pvd[156:190]
        rext, rsz = struct.unpack("<I", rr[2:6])[0], struct.unpack("<I", rr[10:14])[0]
        q, seen = [("/", rext, rsz)], set()
        while q:
            path, ext, sz = q.pop(0)
            if (ext, sz) in seen: continue
            seen.add((ext, sz))
            for nb, e, s, fl in parse_dir(fh, ext, sz):
                nm = clean(nb)
                if nm in (".", ".."): continue
                full = (path.rstrip("/") + "/" + nm) if path != "/" else ("/" + nm)
                if full.lower() == TARGET.lower():
                    return e, s
                if fl & 0x02:
                    q.append((full, e, s))
    raise FileNotFoundError(TARGET)

print(f"ORIG: {os.path.abspath(ORIG)}")
print(f"TEST: {os.path.abspath(TEST)}")
ext, sz = find_target(ORIG)
print(f"TOC lookup: {TARGET} extent={ext} size={sz}")
assert sz == 5580, sz
mod = open(MOD, "rb").read()
assert len(mod) == sz

if not os.path.exists(TEST) or os.path.getsize(TEST) != os.path.getsize(ORIG):
    print("copying ISO (1GB, one time)...")
    shutil.copyfile(ORIG, TEST)
    print("copy done")
else:
    print("test ISO already exists with same size; reusing (will re-apply patch)")

with open(TEST, "r+b") as fh:
    fh.seek(ext * SECTOR)
    fh.write(mod)
    fh.flush()
print(f"patched {sz} bytes at LBA {ext} (file offset {ext*SECTOR})")

# verify re-read
with open(TEST, "rb") as fh:
    fh.seek(ext * SECTOR)
    back = fh.read(sz)
print(f"reextract sha: {hashlib.sha256(back).hexdigest()}")
print(f"expected  sha: {hashlib.sha256(mod).hexdigest()}")
ok = back == mod
print(f"ISO_INSERT_VERIFY = {'PASS' if ok else 'FAIL'}")

# full chunked diff orig vs test (expect exactly 6 bytes)
mis, first, last, total = 0, None, None, 0
with open(ORIG, "rb") as a, open(TEST, "rb") as b:
    off = 0
    while True:
        ca, cb = a.read(1 << 20), b.read(1 << 20)
        if not ca and not cb: break
        assert len(ca) == len(cb)
        for i in range(len(ca)):
            if ca[i] != cb[i]:
                mis += 1
                if first is None: first = off + i
                last = off + i
        off += len(ca)
        total = off
print(f"iso sizes: {total} bytes; differing bytes orig-vs-test: {mis}; first={first} last={last}")
with open("logs/stage04/iso_insert_report.txt", "w", encoding="utf-8") as f:
    f.write(f"ORIG: {os.path.abspath(ORIG)}\nTEST: {os.path.abspath(TEST)}\n")
    f.write(f"target: {TARGET} extent={ext} size={sz}\n")
    f.write(f"modified .loc sha: {hashlib.sha256(mod).hexdigest()}\n")
    f.write(f"reextract sha: {hashlib.sha256(back).hexdigest()}\n")
    f.write(f"ISO_INSERT_VERIFY = {'PASS' if ok else 'FAIL'}\n")
    f.write(f"orig-vs-test differing bytes: {mis} first={first} last={last} total={total}\n")
print("wrote logs/stage04/iso_insert_report.txt")
