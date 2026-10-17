"""Stage02: header + strings sampling for max 3 candidate files only.
Read-only. Reads file-data extents but ONLY first 4KB + tiny samples.
Never extracts archives fully, never modifies ISO.
Targets (from Stage01):
  /PSP_GAME/USRDIR/data/locale/trc/eng_us.loc
  /PSP_GAME/USRDIR/data/fonts.arc
  /PSP_GAME/USRDIR/data/index.ind
"""
import os, struct, json, re

ISO = None
for f in os.listdir("."):
    if f.lower().endswith(".iso"):
        ISO = f
        break
assert ISO, "no iso"
SECTOR = 2048
TARGETS = [
    "/PSP_GAME/USRDIR/data/locale/trc/eng_us.loc",
    "/PSP_GAME/USRDIR/data/fonts.arc",
    "/PSP_GAME/USRDIR/data/index.ind",
]
HEADER_N = 4096
MAX_STRINGS = 100

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

def clean(name_raw):
    if name_raw == b"\x00":
        return "."
    if name_raw == b"\x01":
        return ".."
    s = name_raw.decode("utf-8", errors="replace")
    if ";1" in s:
        s = s.split(";1")[0]
    return s

def build_index(fh):
    fh.seek(16 * SECTOR)
    pvd = fh.read(SECTOR)
    root_rec = pvd[156:190]
    root_ext = struct.unpack("<I", root_rec[2:6])[0]
    root_sz = struct.unpack("<I", root_rec[10:14])[0]
    idx = {}  # lower path -> (extent, size, is_dir)
    queue = [("/", root_ext, root_sz)]
    seen = set()
    while queue:
        path, ext, sz = queue.pop(0)
        if (ext, sz) in seen:
            continue
        seen.add((ext, sz))
        for name_raw, e, s, flags in parse_dir(fh, ext, sz):
            nm = clean(name_raw)
            if nm in (".", ".."):
                continue
            full = (path.rstrip("/") + "/" + nm) if path != "/" else ("/" + nm)
            is_dir = bool(flags & 0x02)
            idx[full.lower()] = (e, s, is_dir, full)
            if is_dir:
                queue.append((full, e, s))
    return idx

def hexdump(data, width=16, max_lines=16):
    lines = []
    for i in range(0, min(len(data), width*max_lines), width):
        chunk = data[i:i+width]
        hx = " ".join(f"{b:02x}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{i:08x}  {hx:<{width*3}}  |{asc}|")
    if len(data) > width*max_lines:
        lines.append(f"... +{len(data)-width*max_lines} more bytes")
    return "\n".join(lines)

def ascii_strings(data, minlen=4, limit=100):
    out = []
    cur = []
    start = 0
    for i, b in enumerate(data):
        if 32 <= b < 127 or b in (9, 10, 13):
            if not cur:
                start = i
            cur.append(b)
        else:
            if len(cur) >= minlen:
                # require at least 2 letters/digits to reduce noise
                txt = bytes(cur).decode("ascii", errors="replace")
                out.append((start, txt))
                if len(out) >= limit:
                    break
            cur = []
    if cur and len(out) < limit and len(cur) >= minlen:
        out.append((start, bytes(cur).decode("ascii")))
    return out

def utf16le_strings(data, minlen=4, limit=100):
    out = []
    # scan on 2-byte units; require printable ascii range + common punct
    n = len(data) // 2 * 2
    cur = []
    start = 0
    for i in range(0, n, 2):
        lo, hi = data[i], data[i+1]
        if hi == 0 and (32 <= lo < 127 or lo in (9, 10, 13)):
            if not cur:
                start = i
            cur.append(lo)
        else:
            if len(cur) >= minlen:
                out.append((start, bytes(cur).decode("ascii")))
                if len(out) >= limit:
                    break
            cur = []
    if cur and len(out) < limit and len(cur) >= minlen:
        out.append((start, bytes(cur).decode("ascii")))
    return out

def u32_views(data, count=16):
    le = []
    be = []
    for i in range(0, min(len(data), count*4), 4):
        le.append(struct.unpack("<I", data[i:i+4])[0])
        be.append(struct.unpack(">I", data[i:i+4])[0])
    return le, be

results = {}
with open(ISO, "rb") as fh:
    idx = build_index(fh)
    for t in TARGETS:
        key = t.lower()
        info = {"target": t, "found": key in idx}
        if key not in idx:
            results[t] = info
            continue
        ext, sz, is_dir, real = idx[key]
        info.update({"real_path": real, "extent": ext, "size": sz, "is_dir": is_dir})
        n = min(sz, HEADER_N)
        fh.seek(ext * SECTOR)
        head = fh.read(n)
        info["header_len"] = len(head)
        info["magic16_hex"] = head[:16].hex()
        info["magic16_ascii"] = "".join(chr(b) if 32 <= b < 127 else "." for b in head[:16])
        info["first64_hex"] = head[:64].hex()
        le, be = u32_views(head, 16)
        info["u32le_first16"] = le
        info["u32be_first16"] = be
        # null / text heuristics on header window
        info["null_ratio_h"] = round(head.count(0) / max(1, len(head)), 4)
        info["printable_ratio_h"] = round(sum(1 for b in head if 32 <= b < 127) / max(1, len(head)), 4)
        # strings sampling within header window only (stage limit: small sample)
        info["ascii_100"] = [{"off": o, "s": s[:160]} for o, s in ascii_strings(head, 4, MAX_STRINGS)]
        info["utf16le_100"] = [{"off": o, "s": s[:160]} for o, s in utf16le_strings(head, 4, MAX_STRINGS)]
        info["n_ascii"] = len(info["ascii_100"])
        info["n_utf16le"] = len(info["utf16le_100"])
        # offset-table plausibility: count of u32 LE values that fall inside file size (and are increasing runs)
        if len(head) >= 64:
            vals = [struct.unpack("<I", head[i:i+4])[0] for i in range(0, min(len(head), 512), 4)]
            inside = [v for v in vals if 0 < v < sz]
            info["table_check_first128_u32_inside_filesize"] = len(inside)
            info["table_vals_sample"] = vals[:32]
        # extra mid-file 4KB sample offsets (1 sample each, to avoid full read)
        info["mid_samples"] = []
        for frac, label in [(0.5, "mid"), (0.9, "tail-4k")]:
            if sz > HEADER_N * 2:
                if label == "mid":
                    off = ext * SECTOR + int(sz * frac)
                else:
                    off = ext * SECTOR + sz - min(sz, 2048)
                fh.seek(off)
                samp = fh.read(2048)
                a = ascii_strings(samp, 5, 20)
                u = utf16le_strings(samp, 5, 20)
                info["mid_samples"].append({
                    "label": label, "file_off": off - ext * SECTOR,
                    "null_ratio": round(samp.count(0) / max(1, len(samp)), 4),
                    "ascii_n": len(a), "ascii_ex": [s[:120] for _, s in a[:10]],
                    "utf16_n": len(u), "utf16_ex": [s[:120] for _, s in u[:10]],
                })
        # save header hexdump to text file
        safe = t.strip("/").replace("/", "__")
        with open(f"logs/stage02/{safe}.hexdump.txt", "w", encoding="utf-8") as hf:
            hf.write(f"target: {t}\nreal: {real}\nextent={ext} size={sz}\n")
            hf.write(f"header bytes read: {len(head)}\n\n")
            hf.write(hexdump(head, 16, 256) + "\n\n")
            hf.write("u32 LE first16:\n" + " ".join(str(x) for x in le) + "\n")
            hf.write("u32 BE first16:\n" + " ".join(str(x) for x in be) + "\n")
        results[t] = info

with open("logs/stage02/results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# console: short preview only
for t in TARGETS:
    r = results[t]
    print("=" * 70)
    print(t, r.get("size"), "extent", r.get("extent"))
    if not r.get("found"):
        print("NOT FOUND"); continue
    print("magic16:", r["magic16_hex"], "|", r["magic16_ascii"])
    print(f"null_ratio={r['null_ratio_h']} printable={r['printable_ratio_h']}")
    print(f"ascii_n={r['n_ascii']} utf16_n={r['n_utf16le']}")
    for e in r["ascii_100"][:15]:
        print(f"  A@{e['off']:04x}: {e['s'][:100]}")
    for e in r["utf16le_100"][:10]:
        print(f"  U@{e['off']:04x}: {e['s'][:100]}")
    for m in r.get("mid_samples", []):
        print(f"  [{m['label']}@{m['file_off']}] null={m['null_ratio']} ascii_n={m['ascii_n']}")
        for s in m["ascii_ex"][:5]:
            print(f"    - {s[:100]}")
print("wrote logs/stage02/results.json + hexdumps")
