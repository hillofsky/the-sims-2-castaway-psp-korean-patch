## LATEST: screenshot render fixes FINAL_20261017_R5
2026-10-17T16:50:57.203439+09:00
DXT3 alpha corrected (R3 incorrectly encoded BC3); title signed y bearing fixed; new Korean sizes9/10/11 and matching title/glow11. Main13430/save52/movie1 drafts retained. Build+delta reproduction passed; post-build render_fix_checks.json passed. NO emulator/runtime QA. SHA256 03b8aa99ddc753e9324463e556b7055bb364a72a5a6152e514a88cdf267bebb4. R4 intermediate is NOT a delivery. See FINAL_HANDOFF.md, logs/FIX_084/fix_summary.json.

## LATEST DELIVERY: FINAL_20261017_R3 — identified assets first draft
2026-10-17T15:14:13.441700+09:00
ISO SHA256 883e95f5db802310924f4ac5875302c07ded94d05267d40d0a213c6c3582124c; main13430,save/load52,movie caption1 drafts;1224 nonASCII chars. All identified linguistic table rows resolved; proper names, controls and technical literals preserved. Textures3374 surveyed,8 image/movie draft entries,12 ISO files replaced. Build and exact patch reproduction succeeded; NO emulator/runtime QA. Source handoff is modular and includes FFmpeg-dependent PMF builders. User owns runtime review. This build supersedes FINAL_R2 and all source checkpoints below. It was built because identified first-draft scope finished, not because quota was below5%. Remaining usage last19%primary/33%weekly. See FINAL_HANDOFF.md and translation/ASSET_SCOPE_083.md. No further ChatGPT messages or GitHub upload were sent.

# Castaway Korean localization

Current experimental build STEP028:1901 Korean DRAFT rows /16550 extracted English rows,580 added characters. Build and patch reproduction passed; newest recipe/tool/action rows need runtime review. Earlier menu/tutorial/save/load screens passed limited checks. Full game remains unfinished.

Read PROJECT_STATE.md and HANDOFF_NEXT.md before continuing. Original ISO and Korean Sims2 reference remain local and unchanged.

## Reproduce a build
Python 3.9+ and Pillow are required for font rasterization. Configure local input paths and font in config/project.json. Font source is local Windows Malgun Gothic; its TTF is not included.

```powershell
python -m pip install -r requirements.txt
.\run.ps1 -Mode Build -BuildId NEW_UNIQUE_ID -VerifyPatch
```

This validates input SHA256 and translation tokens, rebuilds quickdat/fonts/dataset clones/global index, appends ISO resources, creates a copy/literal patch and optionally reproduces it. A new build ID is mandatory. Logs and a result ZIP are produced, including on failure (fall_ prefix). No editorial batches are applied implicitly.

```powershell
.\run.ps1 -Mode Analyze
.\run.ps1 -Mode Package -BuildId STEP024
```

Analyze refreshes extraction/context while preserving existing drafts. Canonical translations are in translation/text_master.tsv. Apply glossary/batches deliberately: batches can overwrite existing mapped draft rows. Existing-allocation overflow is informational because string pools are rebuilt; duplicate IDs/token mismatches fail validation.

## Apply a packaged patch
Only Python standard library and the exact original ISO are needed:

```powershell
python scripts/apply_binary_patch.py --source "PATH_TO_ORIGINAL.iso" --patch "build/CASTAWAY_STEP024_EXPERIMENTAL.patch.zip" --output "NEW_OUTPUT.iso"
```

The applier verifies source, literal payload and full output SHA256; existing output paths are rejected. A matching hash proves binary reproduction, while runtime QA is tracked separately.

## Modules
src/castaway separates ISO metadata, ARC/BIG/RefPack, quickdat, dataset envelopes, global index, fonts, ISO insertion, copy/literal delta, configuration and debugger transport.

Both quickdat and embedded dataset clones must change. Resized archive records require index.ind updates. Fonts preserve original glyph pixels and extend atlases up to512x512; title glyph stride conversion is essential.

Runtime scripts validate owned PID/start time/executable/port/game ID. Visible tests use PPSSPP1.19.3 with --graphics=software. runtime_control.py frame captures actual PSP VRAM; pressframes sends acknowledged button presses/releases. Obtain PPSSPP separately; emulator binaries are not packaged.

## Publication preparation
Source, configuration, translation data, documentation and generated patch are separated. ISO files, extracted assets, large dumps, downloaded emulator binaries and temporary builds are ignored. Review translation quality, patch content, font redistribution conditions and choose a license before publishing. No GitHub publication performed.

Independent format references: https://github.com/actioninja/refpack-rs ; https://aluigi.altervista.org/bms/sims2_psp.bms ; https://github.com/AndyGura/nfs-resources-converter/blob/main/resources/NFS3.md . Compatibility is established through local bytes and roundtrip checks.

Latest reproducible build STEP025 is byte-identical to STEP024; complete run.ps1 Build/VerifyPatch/Package and repeated-ID failure packaging passed. config/project.json latest_build_id selects default candidate. Patch: build/CASTAWAY_STEP025_EXPERIMENTAL.patch.zip.

STEP026 latest:1132 drafts/534 characters, including419 rows for130 recipe names. SHA25685a2ce1d5ca759a906c74bd5fb09cc6b57d61dc5230456ab63c9e935525e2959.276939-byte patch reproduced exactly. Boot/main menu reviewed; new recipe names unverified. Use config.latest_build_id and this latest checkpoint over earlier build references.

Packaging repair: use a newly generated STEP028 handoff. Earlier compact packages omitted text_master.tsv due a size filter. The repaired packager requires the canonical TSV and verifies all manifest hashes.
