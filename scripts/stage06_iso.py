"""Stage06 Tasks 5-6: same-size insert (Stage04 method), re-extract verify."""
import os, struct, hashlib, shutil, sys
sys.path.insert(0, "logs/stage03")
from parse_loc import parse_loc
ORIG = "Sims 2, The - Castaway (USA) (En,Fr,De,Es,It,Nl,Pt).iso"
TEST = "The_Sims_2_STAGE06_RENDER.iso"
MOD = "logs/stage06/eng_us_render_test.loc"
SECTOR, LBA, SZ = 2048, 275296, 5580
assert not os.path.exists(TEST), "refusing overwrite"
mod = open(MOD, "rb").read()
assert len(mod) == SZ
shutil.copyfile(ORIG, TEST)
with open(TEST, "r+b") as fh:
    fh.seek(LBA * SECTOR)
    fh.write(mod)
with open(TEST, "rb") as fh:
    fh.seek(LBA * SECTOR)
    back = fh.read(SZ)
ok = back == mod
r = parse_loc(TEST and MOD) if False else parse_loc(MOD)
print(f"reextract==build: {ok} sha={hashlib.sha256(back).hexdigest()}")
r2 = None
# parse the re-extracted bytes via temp file to prove ISO content parses
open("logs/stage06/eng_us_reextract.loc", "wb").write(back)
r2 = parse_loc("logs/stage06/eng_us_reextract.loc")
ok = ok and r2["ok"] == 52 and r2["entries"][5]["text"] == "TEST %s"
print(f"ISO_RENDER_INSERT = {'PASS' if ok else 'FAIL'}")
open("logs/stage06/iso_insert_report.txt", "w").write(
    f"ORIG: {os.path.abspath(ORIG)}\nTEST: {os.path.abspath(TEST)}\nLBA={LBA} size={SZ}\n"
    f"reextract sha={hashlib.sha256(back).hexdigest()}\nISO_RENDER_INSERT = {'PASS' if ok else 'FAIL'}\n")
