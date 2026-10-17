"""Stage01: PSP ISO top-level structure via ISO9660 TOC only.
Reads ONLY: file metadata, PVD (2KB), directory sectors.
Never reads file contents, never scans whole ISO, never extracts.
"""
import os, sys, struct, json, collections

ISO_PATH = None
# auto-detect single .iso in cwd
for f in os.listdir("."):
    if f.lower().endswith(".iso"):
        ISO_PATH = f
        break
if ISO_PATH is None:
    print("ERROR: no iso found", file=sys.stderr)
    sys.exit(1)

SECTOR = 2048
iso_size = os.path.getsize(ISO_PATH)
print(f"ISO: {ISO_PATH}")
print(f"ISO size bytes: {iso_size}")

with open(ISO_PATH, "rb") as fh:
    # 1) header: first 4096 bytes (system area, no content scan)
    fh.seek(0)
    head = fh.read(4096)
    print(f"header[0:256] hex: {head[:256].hex()[:128]}...")
    # check if first 32KB is zero (normal for ISO)
    nonzero = sum(1 for b in head if b != 0)
    print(f"header first 4096 nonzero bytes: {nonzero}")

    # 2) PVD at sector 16
    fh.seek(16 * SECTOR)
    pvd = fh.read(SECTOR)
    assert len(pvd) == SECTOR, "short PVD read"
    pvd_type = pvd[0]
    pvd_magic = pvd[1:6]
    pvd_ver = pvd[6]
    sys_id = pvd[8:40]
    vol_id = pvd[40:72]
    print(f"PVD type={pvd_type} magic={pvd_magic} ver={pvd_ver}")
    print(f"PVD sys_id={sys_id!r}")
    print(f"PVD vol_id={vol_id!r}")
    assert pvd_magic == b"CD001", f"not ISO9660: {pvd_magic!r}"

    # root dir record at PVD[156:190]
    root_rec = pvd[156:190]
    r_len = root_rec[0]
    root_extent = struct.unpack("<I", root_rec[2:6])[0]
    root_size = struct.unpack("<I", root_rec[10:14])[0]
    root_flags = root_rec[25]
    print(f"root extent sector={root_extent} size={root_size} flags={root_flags} rec_len={r_len}")

    def parse_dir(extent, size):
        """Read only directory sectors, return list of records."""
        fh.seek(extent * SECTOR)
        data = fh.read(size)
        recs = []
        off = 0
        while off < len(data):
            if off + 1 > len(data):
                break
            rl = data[off]
            if rl == 0:
                # pad to next sector
                nxt = ((off // SECTOR) + 1) * SECTOR
                if nxt <= off:
                    nxt = off + 1
                off = nxt
                continue
            if off + rl > len(data):
                break
            rec = data[off:off+rl]
            ext_attr = rec[1]
            extent_l = struct.unpack("<I", rec[2:6])[0]
            size_l = struct.unpack("<I", rec[10:14])[0]
            flags = rec[25]
            nlen = rec[32]
            name_raw = rec[33:33+nlen]
            recs.append({
                "extent": extent_l, "size": size_l, "flags": flags,
                "name_raw": name_raw, "is_dir": bool(flags & 0x02),
            })
            off += rl
        return recs

    def clean_name(name_raw):
        if name_raw == b"\x00":
            return "."
        if name_raw == b"\x01":
            return ".."
        # strip version ";1" and handle Joliet later; keep as decoded
        try:
            s = name_raw.decode("utf-8", errors="replace")
        except Exception:
            s = repr(name_raw)
        # ISO9660 often "NAME.EXT;1"
        if ";1" in s:
            s = s.split(";1")[0]
        return s

    # BFS over directories only
    all_files = []  # (path, size, extent, is_dir)
    dirs_by_depth = {}  # depth -> list
    queue = [("/", root_extent, root_size, 0)]
    visited_extents = set()
    total_dir_bytes = 0
    MAX_DIR_BYTES = 50 * 1024 * 1024

    root_children = []
    level2 = {}  # topdir -> children names

    while queue:
        path, ext, sz, depth = queue.pop(0)
        if (ext, sz) in visited_extents:
            continue
        visited_extents.add((ext, sz))
        if total_dir_bytes + sz > MAX_DIR_BYTES:
            print(f"ABORT: dir bytes exceed {MAX_DIR_BYTES}", file=sys.stderr)
            break
        recs = parse_dir(ext, sz)
        total_dir_bytes += sz
        for r in recs:
            nm = clean_name(r["name_raw"])
            if nm in (".", ".."):
                continue
            full = (path.rstrip("/") + "/" + nm) if path != "/" else ("/" + nm)
            all_files.append((full, r["size"], r["extent"], r["is_dir"]))
            if depth == 0:
                root_children.append((nm, r["size"], r["is_dir"], r["extent"]))
                if r["is_dir"]:
                    queue.append((full, r["extent"], r["size"], depth+1))
                    level2[nm] = []
            elif depth == 1:
                top = path.strip("/").split("/")[0]
                level2.setdefault(top, []).append((nm, r["size"], r["is_dir"]))
                if r["is_dir"]:
                    queue.append((full, r["extent"], r["size"], depth+1))
            else:
                if r["is_dir"]:
                    queue.append((full, r["extent"], r["size"], depth+1))

    print(f"total dir sectors bytes read: {total_dir_bytes}")
    print(f"total entries (files+dirs, excl ./. .): {len(all_files)}")

    # stats
    files_only = [x for x in all_files if not x[3]]
    dirs_only = [x for x in all_files if x[3]]
    print(f"dirs: {len(dirs_only)} files: {len(files_only)}")

    ext_counter = collections.Counter()
    for p, s, e, d in files_only:
        base = p.rsplit("/", 1)[-1]
        if "." in base:
            ext = "." + base.rsplit(".", 1)[-1]
            ext = ext.upper()
            # cap weird long extensions (Joliet long names)
            if len(ext) > 12:
                ext = "(long/no-ext)"
        else:
            ext = "(no-ext)"
        ext_counter[ext] += 1

    top30 = sorted(files_only, key=lambda x: x[1], reverse=True)[:30]

    out = {
        "iso": ISO_PATH, "iso_size": iso_size,
        "pvd_sys": sys_id.decode("ascii", "replace").strip(),
        "pvd_vol": vol_id.decode("ascii", "replace").strip(),
        "root_extent": root_extent, "root_size": root_size,
        "total_dir_bytes": total_dir_bytes,
        "total_entries": len(all_files),
        "n_dirs": len(dirs_only), "n_files": len(files_only),
    }
    with open("logs/stage01/toc.json", "w", encoding="utf-8") as out_f:
        json.dump({
            "meta": out,
            "root_children": [{"name": n, "size": s, "is_dir": d, "extent": e} for n, s, d, e in root_children],
            "level2": {k: [{"name": n, "size": s, "is_dir": d} for n, s, d in v] for k, v in level2.items()},
            "ext_counts": dict(ext_counter.most_common(100)),
            "top30": [{"path": p, "size": s, "extent": e} for p, s, e, d in top30],
            "all_entries": [{"path": p, "size": s, "is_dir": d} for p, s, e, d in all_files],
        }, out_f, ensure_ascii=False, indent=2)

    with open("logs/stage01/findings.txt", "w", encoding="utf-8") as f:
        f.write(f"ISO: {ISO_PATH}\nISO size: {iso_size}\n")
        f.write(f"PVD sys={out['pvd_sys']} vol={out['pvd_vol']}\n")
        f.write(f"root extent={root_extent} size={root_size}\n")
        f.write(f"total entries={len(all_files)} dirs={len(dirs_only)} files={len(files_only)}\n")
        f.write(f"dir bytes read={total_dir_bytes}\n\n")
        f.write("== root (depth1) ==\n")
        for n, s, d, e in root_children:
            f.write(f"{'[DIR]' if d else '     '} {n} size={s} extent={e}\n")
        f.write("\n== depth2 ==\n")
        for k, v in level2.items():
            f.write(f"[{k}] {len(v)} entries\n")
            for n, s, d in v[:60]:
                f.write(f"  {'[DIR]' if d else '     '} {n} size={s}\n")
            if len(v) > 60:
                f.write(f"  ... +{len(v)-60} more\n")
        f.write("\n== ext counts ==\n")
        for e, c in ext_counter.most_common(100):
            f.write(f"{e}: {c}\n")
        f.write("\n== top30 largest ==\n")
        for p, s, e, d in top30:
            f.write(f"{s:>12} {p}\n")

    print("wrote logs/stage01/toc.json + findings.txt")
