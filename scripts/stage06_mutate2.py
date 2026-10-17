"""Stage06 attempt 2: index 35 OK -> QK from ORIGINAL."""
import sys, hashlib
sys.path.insert(0, "logs/stage03")
from parse_loc import parse_loc
from rebuild_loc import build
SRC, DST = "logs/stage03/eng_us_orig.loc", "logs/stage06/eng_us_render_test2.loc"
IDX, OLD, NEW = 35, "OK", "QK"
r = parse_loc(SRC)
assert r["header"]["count_at_locl_plus_12"] == 52 and r["entries"][IDX]["text"] == OLD
texts = [e["text"] for e in r["entries"]]
texts[IDX] = NEW
info = build(texts, SRC, DST)
r2 = parse_loc(DST)
assert r2["ok"] == 52 and r2["fails"] == 0 and r2["size"] == 5580
assert r2["entries"][IDX]["text"] == NEW
o, m = open(SRC, "rb").read(), open(DST, "rb").read()
mis = [i for i in range(len(o)) if o[i] != m[i]]
print(f"mod sha={hashlib.sha256(m).hexdigest()} mismatch={len(mis)} at {mis}")
assert len(mis) == 1, mis  # O->Q low byte only
print("ATTEMPT2_ISOLATED = PASS")
