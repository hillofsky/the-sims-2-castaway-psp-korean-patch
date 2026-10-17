"""Probe eng_us_orig.loc structure (working copy only)."""
import struct
p = "logs/stage03/eng_us_orig.loc"
d = open(p, "rb").read()
print("size", len(d))
def u32(o): return struct.unpack("<I", d[o:o+4])[0]
# header fields
for o in [0x00,0x04,0x08,0x0C,0x10,0x14,0x18,0x1C,0x20,0x24,0x28]:
    print(f"{o:#06x} raw={d[o:o+4].hex()} u32le={u32(o)} ascii={''.join(chr(b) if 32<=b<127 else '.' for b in d[o:o+4])}")
cnt = u32(0x20)
print("count candidate @0x20 =", cnt)
offs = [u32(0x24+i*4) for i in range(cnt)]
print("offs len", len(offs), "first5", offs[:5], "last5", offs[-5:])
print("monotonic?", all(b>a for a,b in zip(offs, offs[1:])))
print("all <5560?", all(0<=v<5560 for v in offs), "min", min(offs), "max", max(offs))
# test LOCL-relative: file_off = 0x14 + raw ?
print("--- LOCL-relative test (raw+0x14) ---")
for i, raw in enumerate(offs[:6]):
    fo = 0x14 + raw
    print(i, f"raw={raw}", f"fo={fo:#x}", "bytes:", d[fo:fo+16].hex(), "u16:", d[fo:fo+20])
print("--- last entries ---")
for i, raw in enumerate(offs[-4:]):
    idx = len(offs)-4+i
    fo = 0x14 + raw
    nxt = 0x14 + offs[idx+1] if idx+1 < len(offs) else len(d)
    print(idx, f"raw={raw} fo={fo:#x} nxt={nxt:#x} alloc={nxt-fo}")
    seg = d[fo:nxt]
    print("   seg hex:", seg.hex()[:160])
# check pool start: 0x24+cnt*4 = ?
t_end = 0x24 + cnt*4
print(f"table end = {t_end:#x} ({t_end}), first fo = {0x14+offs[0]:#x}")
# decode each as utf16le until double-null
fails = 0
for i, raw in enumerate(offs):
    fo = 0x14 + raw
    nxt = 0x14 + offs[i+1] if i+1 < len(offs) else len(d)
    seg = d[fo:nxt]
    # find 00 00 terminator
    ti = seg.find(b"\x00\x00")
    print(i, f"fo={fo:#x} nxt={nxt:#x} term_at={ti} seglen={len(seg)}")
    if i > 8:
        print("   ... (truncated)")
        break
