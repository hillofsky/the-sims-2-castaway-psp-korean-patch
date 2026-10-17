"""Re-extract eng_us.loc from STAGE05 test ISO via TOC, parse-verify."""
import struct, sys
sys.path.insert(0, "logs/stage03")
from parse_loc import parse_loc
ISO = "The_Sims_2_STAGE05_VARIABLE.iso"
OUT = "logs/stage05/eng_us_reextract.loc"
SECTOR = 2048
with open(ISO, "rb") as fh:
    fh.seek(REC := 0x118D4)
    rec = fh.read(58)
    ext = struct.unpack("<I", rec[2:6])[0]
    sz = struct.unpack("<I", rec[10:14])[0]
    print(f"record: extent={ext} size={sz}")
    fh.seek(ext * SECTOR)
    data = fh.read(sz)
open(OUT, "wb").write(data)
r = parse_loc(OUT)
print(f"size={r['size']} count={r['header']['count_at_locl_plus_12']} ok={r['ok']} fails={r['fails']}")
print(f"index8={r['entries'][8]['text']!r}")
assert r["size"] == 5574 and r["ok"] == 52 and r["fails"] == 0 and r["entries"][8]["text"] == "OK!"
print("REEXTRACT_PARSE = PASS")
