"""Stage06 attempt-2 ISO (same-size insert)."""
import os, hashlib, shutil
ORIG = "Sims 2, The - Castaway (USA) (En,Fr,De,Es,It,Nl,Pt).iso"
TEST = "The_Sims_2_STAGE06_RENDER2.iso"
MOD = "logs/stage06/eng_us_render_test2.loc"
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
print(f"reextract==build: {ok}")
open("logs/stage06/iso_insert_report2.txt", "w").write(
    f"TEST: {os.path.abspath(TEST)}\nLBA={LBA} size={SZ}\n"
    f"reextract sha={hashlib.sha256(back).hexdigest()}\nISO_RENDER_INSERT2 = {'PASS' if ok else 'FAIL'}\n")
