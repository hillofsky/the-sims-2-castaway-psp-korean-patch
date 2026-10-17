"""Stage05 Tasks 2-4: header compare, offset relocation TSV, payload integrity TSV."""
import struct, hashlib, sys
sys.path.insert(0, "logs/stage03")
from parse_loc import parse_loc

O, M = "logs/stage03/eng_us_orig.loc", "logs/stage05/eng_us_variable.loc"
ro, rm = parse_loc(O), parse_loc(M)
do, dm = open(O, "rb").read(), open(M, "rb").read()
assert len(do) == 5580 and len(dm) == 5574

def u32(d, o):
    return struct.unpack("<I", d[o:o+4])[0]

with open("logs/stage05/header_compare.txt", "w", encoding="utf-8") as f:
    f.write("field | orig_off | orig_raw | orig_val | mod_val | changed\n")
    rows = [
        ("LOCH magic", 0x00, do[0:4].hex(), do[0:4], dm[0:4]),
        ("LOCH+0x04 locl_off", 0x04, do[4:8].hex(), u32(do, 4), u32(dm, 4)),
        ("LOCH+0x08 unk", 0x08, do[8:12].hex(), u32(do, 8), u32(dm, 8)),
        ("LOCH+0x0C ver", 0x0C, do[12:16].hex(), u32(do, 12), u32(dm, 12)),
        ("LOCH+0x10", 0x10, do[16:20].hex(), u32(do, 16), u32(dm, 16)),
        ("LOCL magic", 0x14, do[20:24].hex(), do[20:24], dm[20:24]),
        ("LOCL size @0x18", 0x18, do[24:28].hex(), u32(do, 24), u32(dm, 24)),
        ("LOCL+0x1C unk", 0x1C, do[28:32].hex(), u32(do, 28), u32(dm, 28)),
        ("count @0x20", 0x20, do[32:36].hex(), u32(do, 32), u32(dm, 32)),
    ]
    for name, off, hx, ov, mv in rows:
        ovs = ov.hex() if isinstance(ov, bytes) else str(ov)
        mvs = mv.hex() if isinstance(mv, bytes) else str(mv)
        f.write(f"{name} | {off:#06x} | {hx} | {ovs} | {mvs} | {ovs != mvs}\n")
    f.write(f"file size | - | - | {len(do)} | {len(dm)} | True\n")
    f.write(f"LOCL size == filesize-20: orig {u32(do,24)}=={len(do)-20} mod {u32(dm,24)}=={len(dm)-20}\n")
    f.write(f"table_off orig={ro['header']['table_off']} mod={rm['header']['table_off']} (must be equal)\n")
    f.write(f"pool_off orig={ro['header']['pool_off']} mod={rm['header']['pool_off']} (must be equal)\n")

eo, em = ro["entries"], rm["entries"]
delta8 = em[8]["allocated_bytes"] - eo[8]["allocated_bytes"]
print(f"index8 alloc {eo[8]['allocated_bytes']} -> {em[8]['allocated_bytes']} (delta {delta8})")
with open("logs/stage05/offset_compare.tsv", "w", encoding="utf-8") as f:
    f.write("index\toriginal_raw_offset\tmodified_raw_offset\tdelta\texpected_delta\tpass\n")
    for k in range(52):
        o_raw, m_raw = eo[k]["raw_offset"], em[k]["raw_offset"]
        d = m_raw - o_raw
        exp = 0 if k <= 8 else delta8
        ok = (d == exp)
        f.write(f"{k}\t{o_raw}\t{m_raw}\t{d}\t{exp}\t{ok}\n")
        if not ok:
            print(f"OFFSET MISMATCH idx {k}: delta {d} expected {exp}")

with open("logs/stage05/payload_integrity.tsv", "w", encoding="utf-8") as f:
    f.write("index\torig_text_esc\tmod_text_esc\torig_payload_sha\tmod_payload_sha\tpass\n")
    def esc(s):
        return s.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t") if s is not None else ""
    for k in range(52):
        ot, mt = eo[k]["text"], em[k]["text"]
        oh = hashlib.sha256(ot.encode("utf-16-le")).hexdigest() if ot is not None else ""
        mh = hashlib.sha256(mt.encode("utf-16-le")).hexdigest() if mt is not None else ""
        exp_pass = (oh == mh) if k != 8 else (oh != mh)
        f.write(f"{k}\t{esc(ot)}\t{esc(mt)}\t{oh}\t{mh}\t{exp_pass}\n")
        if not exp_pass:
            print(f"PAYLOAD MISMATCH idx {k}")
print("wrote header_compare.txt offset_compare.tsv payload_integrity.tsv")
