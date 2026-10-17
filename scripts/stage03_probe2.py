"""Probe terminator/padding for all 52 entries (working copy only)."""
import struct
d = open("logs/stage03/eng_us_orig.loc","rb").read()
locl_off = struct.unpack("<I", d[4:8])[0]
cnt = struct.unpack("<I", d[locl_off+12:locl_off+16])[0]
print("locl_off", locl_off, "cnt", cnt)
offs = [struct.unpack("<I", d[locl_off+16+i*4:locl_off+20+i*4])[0] for i in range(cnt)]
from collections import Counter
c = Counter()
for i, raw in enumerate(offs):
    fo = locl_off + raw
    nxt = locl_off + offs[i+1] if i+1 < cnt else len(d)
    alloc = nxt - fo
    seg = d[fo:nxt]
    # aligned u16 scan
    units = [struct.unpack("<H", seg[j:j+2])[0] for j in range(0, len(seg), 2)]
    try:
        ti = units.index(0)
    except ValueError:
        print(i, "NO TERMINATOR", fo, alloc, seg.hex()[:80])
        continue
    text_units = units[:ti]
    rest = units[ti:]
    # rest[0] is terminator; rest[1:] padding (should be zeros)
    nonz = [u for u in rest[1:] if u != 0]
    c[(alloc, len(text_units)*2, len(rest)*2)] += 1
    if rest[1:] and any(u != 0 for u in rest[1:]):
        print(i, "NONZERO PAD", fo, alloc, rest)
    # decode check
    try:
        s = bytes(seg[:ti*2]).decode("utf-16-le")
    except Exception as e:
        print(i, "DECODE FAIL", e)
    if i < 6 or alloc % 2 == 1 or len(rest)*2 not in (2, 4):
        print(i, f"fo={fo:#x} alloc={alloc} textlen={len(text_units)*2} rest={len(rest)*2} text={s[:40]!r}")
print("dist (alloc,textbytes,restbytes)->n:", dict(c))
# check fo alignment
print("fo mod 4:", Counter((locl_off+r) % 4 for r in offs))
print("alloc mod 4:", Counter(((locl_off+offs[i+1] if i+1<cnt else len(d))-(locl_off+r)) % 4 for i, r in enumerate(offs)))
