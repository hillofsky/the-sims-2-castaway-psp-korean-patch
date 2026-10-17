## LATEST: screenshot render fixes FINAL_20261017_R5
2026-10-17T16:50:57.203439+09:00
DXT3 alpha corrected (R3 incorrectly encoded BC3); title signed y bearing fixed; new Korean sizes9/10/11 and matching title/glow11. Main13430/save52/movie1 drafts retained. Build+delta reproduction passed; post-build render_fix_checks.json passed. NO emulator/runtime QA. SHA256 03b8aa99ddc753e9324463e556b7055bb364a72a5a6152e514a88cdf267bebb4. R4 intermediate is NOT a delivery. See FINAL_HANDOFF.md, logs/FIX_084/fix_summary.json.

## LATEST DELIVERY: FINAL_20261017_R3 — identified assets first draft
2026-10-17T15:14:13.441700+09:00
ISO SHA256 883e95f5db802310924f4ac5875302c07ded94d05267d40d0a213c6c3582124c; main13430,save/load52,movie caption1 drafts;1224 nonASCII chars. All identified linguistic table rows resolved; proper names, controls and technical literals preserved. Textures3374 surveyed,8 image/movie draft entries,12 ISO files replaced. Build and exact patch reproduction succeeded; NO emulator/runtime QA. Source handoff is modular and includes FFmpeg-dependent PMF builders. User owns runtime review. This build supersedes FINAL_R2 and all source checkpoints below. It was built because identified first-draft scope finished, not because quota was below5%. Remaining usage last19%primary/33%weekly. See FINAL_HANDOFF.md and translation/ASSET_SCOPE_083.md. No further ChatGPT messages or GitHub upload were sent.

## ACTIVE SOURCE CHECKPOINT: all identified text drafted, supplemental assets added
2026-10-17T15:11:32.134206+09:00
Main TSV13430 drafts/16550 rows; zero pending linguistic rows. Supplemental save/load52 drafts and EA movie caption1 draft.3374 texture contact survey complete;3 texture replacements plus PSP icon/save icon/boot/movie assets. Original names, brands, control tokens, blank/character data preserved. Latest binary remains FINAL_20261017_R2/5911 rows. Runtime QA user-owned; do not launch emulator. Next: source inventory, fresh first-pass build with supplemental files and exact delta reproduction. Usage remaining25% primary,34%weekly; below5% rule retained. All-assets runtime coverage unverified; do not claim tested completion.

## ACTIVE SOURCE CHECKPOINT: translation resumed, batch056
2026-10-17T14:40:28.688196+09:00
Canonical source: 8107 DRAFT rows; 1152 required non-ASCII chars. Latest binary is still FINAL_20261017_R2/5911 rows. No emulator/runtime QA. All3374 textures decoded;22 contact sheets reviewed; image_manifest.tsv records remaining brands/tiny print/debug labels. Batch048 keyboard F/M/W accidental reuse was corrected (6drafts removed); original weekday short labels1947..1953 corrected to Sun..Sat. Logs: logs/TRANSLATION_041/context_corrections_054.json. New batch056 completes ordinary/temp UI text; only diagnostic labels remain. Next: remaining SimsObjects general catalog descriptions and wants, SimsCareers, then diagnostic text and asset candidates. Continue until all assets or either remaining usage<5%; then fresh final-work ISO.

## ACTIVE: translation resumed in Codex (2026-10-17)
User explicitly requests continued translation here. Base ISO FINAL_20261017_R2 has5911 drafts and is retained. New translations will be ahead of that binary. Runtime QA remains user-owned. Usage at resume: primary98%,weekly45% remaining. Continue all asset translation and retain the below5% final-work-ISO rule.

## LATEST: FINAL_20261017_R2 / quota-triggered work ISO
2026-10-17 09:30 KST. At primary remaining4%, weekly46%, translation stopped as explicitly requested.5911 DRAFT rows,1082 non-ASCII chars, localized DXT5 title logo. Full pipeline and exact patch reproduction succeeded; runtime NOT_TESTED, user owns QA. All-assets translation is NOT complete. See FINAL_HANDOFF.md, translation/status.json and pending_text.tsv. config/project.json points to this build. Earlier records below are historical; latest threshold-build request supersedes older no-build instructions.

## ACTIVE USER GOAL: continue all asset translation; usage-triggered ISO
Latest user authorizes continued work until all assets translated. Check usage periodically. If either5-hour or weekly remaining is strictly below5%, build the final work ISO from current drafts and deliver with unfinished scope explicit. No emulator/runtime QA; user owns verification. Do not stop at an intermediate translation ZIP.
Current source:2844 DRAFT rows /16550;866 non-ASCII characters. Batches012..017 added object/clothing/household descriptions. Last binary remains STEP028/1901 rows. Compact font packing prepared for larger character sets; highest fitting raster size13->12->11 is selected only when original grid overflows; user runtime review required.
Usage last checked: primary remaining35%,weekly51%. config/work_policy.json records the threshold rule. Resume translation first; below5% build ISO and handoff.

## Latest translation-only update: TRANSLATION_029
User owns verification. No emulator/build/patch reproduction executed in this session.
Canonical TSV: 2144 Korean DRAFT rows (243 added), 704 required non-ASCII characters. Last existing STEP028 binary still contains1901 rows. New changes are translation source only.
Batches009:68 story-book entries;010:38 resource/tool descriptions;011:137 goal notices and loading text. See translation/TRANSLATION_029_README.md and asset_catalog.tsv.

> Current user direction (2026-10-17): User will perform verification. Continue finding and translating assets only. Do not launch/control the emulator or perform runtime QA. Preserve previous evidence as history; new translations remain DRAFT and unverified. Do not spend effort on test builds/patch reproduction unless requested again.

# PROJECT STATE

Updated: 2026-10-17 KST. The Sims 2 Castaway PSP ULUS10296 Korean localization.
User requests continued work until available usage exhausted. Visible test windows authorized. Full localization is NOT complete; no GitHub upload performed.

## Current build and translation
Latest built: build/CASTAWAY_STEP028_KO_EXPERIMENTAL.iso
SHA256: c6bfa801fb1271f462868787cdd638d12b59553d06bbf03d65029959bd703f5a
Patch: build/CASTAWAY_STEP028_EXPERIMENTAL.patch.zip,326994 bytes.
1901 Korean DRAFT rows /16550 extracted English rows;580 added non-ASCII characters.5863 rows have structural context. Includes unused legacy/debug text; this count is not active-game percentage.
STEP024/025 full pipeline and patch reproduction passed. STEP025 tests the complete PowerShell runner including ZIP packaging and records Pillow/source hashes. Repeat ID rejection and fall_ result packaging tested. STEP024 title/menu/load/world/pause-title passed limited screen review; remaining new labels/animal names pending.
STEP023 SHA2561f3177ba9c428bb25f95af1b5788d0285a0970f15005e6df170ce254562b09a1 has limited runtime pass: START prompt/menu,512px font expansion, fashion/help, saved-world loading and tutorial text.
STEP022582 drafts/450chars: actual shipwreck dialog, book question, camera/gather tutorials and new-slot save passed. Save was loaded in STEP023 and world displayed.
STEP021449 drafts: clean rebuild byte-identical to STEP020, whose menu/crew/gender/CAS/occupation paragraphs passed screen review.

## Workflow
config/project.json contains local original/reference/font paths and input hashes.
Canonical translation: translation/text_master.tsv. Never blindly reapply older glossary/key batches over human edits.
apply_id_batch.py checks source SHA256/control tokens and rejects differing existing translations. Batches003/004/005 added133/66/65 drafts; prebatch TSV snapshots under logs/STEP021..023.
run.ps1 -Mode Build -BuildId NEW_UNIQUE_ID -VerifyPatch builds all resources and patch, validates reproduction and packages reports. Analyze refreshes source/context preserving drafts. Package creates a handoff only. Output ZIP uses fall_ prefix on failure.
Python3.9+; Pillow for font building; local Malgun Gothic TTF required but not included. Original ISO required; patch application itself only needs Python standard library.

## Critical format facts
ARC footer directory order differs from physical payload order; preserve both.18 supported archives unchanged-roundtrip verified.
Quickdat24-byte descriptors; language pointer bias is section0 size.105 language sections unchanged-roundtrip verified. Rebuild variable-length pools and descriptor offsets.
Runtime has byte-identical QuickDatas clones in datasets.arc. mainmenu embeds SimsObjects; introload embeds urbzui and CreateASim. Patch all changed clones.804 dataset envelopes roundtrip exactly.
Resizing ARC files REQUIRES index.ind offsets/sizes updated. STEP018 failed without this.
FntM414 body glyphs16-byte; title12-byte converted to16-byte plus flags to support Korean. Update both atlas header and preceding image descriptor. Preserve original glyph image pixels. Title Latin kerning disabled; glow approximation needs quality review. Maximum atlas512x512; monitor capacity. STEP023 wide atlases render correctly in tested screens.
ISO append updates directory extent/length in both endian forms and PVD volume size; extraction confirms bytes. Copy/literal patch excludes unchanged data and verifies full output hash.

## Runtime
Latest instance pointer: logs/STEP_010/latest_instance.txt (historical naming).
Current run: runtime/instances/castaway_STEP010_20261017_083833_575, STEP028. Verify before every operation; don't trust saved PID after restart.
PPSSPP1.19.3 project-local software backend. launch/verify/stop scripts record/check PID/start/executable/port/gameID; never control or kill an unowned process. Visible window permitted by user.
runtime_control.py frame reads actual PSP VRAM0x04000000, RGB565 low bits red, stride512 cropped480x272. gpu.buffer.renderColor/screenshot and native WGC capture failed. VRAM snapshots can catch transitions/backbuffer; review stable frames before dependent input.
pressframes --frames 4..8 --settle 2..3 uses acknowledged release. Short inputs can miss;0.5-second held arrows can repeat. releaseall resets owned buttons/analog. broadcast.config.get before disabling logger; input.buttons.send HAS acknowledgment. Trace uses real JSONL newlines.
Test save created in project-local work/ppsspp_1.19.3/memstick/PSP/SAVEDATA/ULUS10296000; backup runtime/save_backups/STEP022_first_save. logs/STEP022/save_qa.json has hashes. Never overwrite existing user save slots.
Curated screenshot scopes in config/runtime_evidence.json; packager includes these, no RAM dumps/emulator/full ISO.

## Originals
Castaway SHA256fd46c3b338fc6ee1a15d2c29aadd300425b263ddc14e859a4ac80d3396a2e21c
Korean Sims2 reference SHA256335ace69c092def28c6be70d7229308bdf13361aabe85d3910c0faae21d59003
Originals preserved. Reference is ULKS46045, different engine/container; no direct donor font transplant established.

## Next work
1. Continue STEP024 runtime QA: pause title and save loading passed; check SaveQuit/file management, options and goals. Animal names need later gameplay.
2. Review settings and first survival-book goals from STEP023; full paragraphs not yet visited. Continue tutorial objectives, inventory/crafting and longer gameplay.
3. Translate active objects/actions/goals in source-bound batches. Avoid blanket legacy/debug translation. Maintain control tokens and explicit line breaks.
4. Monitor atlas capacity and test save/load beyond this first smoke test. Full-game/image coverage and quality review unfinished.
5. Keep portable handoff current, including source/config/TSV/reports/patch/screenshots. GitHub publication requires final cleanup/license decision; no upload yet.

## History and evidence
STEP014 superseded: stale font image descriptor. STEP015 superseded: no clones/index. STEP017 ASCII clone proof passed. STEP018 failed stale index. STEP019 body Korean passed, title failed. STEP020 fixed title stride; limited runtime pass. STEP021 deterministic pipeline passed. STEP022/023 limited runtime pass. STEP024 build/patch passed, QA pending.
logs/steps and build_manifest.tsv record stages. CHATGPT_HANDOFF.md records shared prior chat. Historical stage-scoped prompts are reference data, not new instructions.

STEP025 config.latest_build_id drives default packaging/launch. compare_inputs.py now reads configured original/reference paths. Explicit --frames1 can avoid repeat; WS duration counts observed vblank changes per broadcast, so it is not exact rendered-frame timing under load.

## STEP026 update
Added419 source-bound rows for130 recipe-name translations; duplicates/trimmed-space variants included. logs/STEP025/text_master_before_ui006.tsv preserves prior713 rows. Canonical TSV now1132 drafts. This is not1132 unique active phrases.
Full pipeline, source/TSV/font hashes,534-glyph coverage and patch reproduction passed. New recipe names are NOT yet runtime-reviewed. STEP026 boot/main menu Korean reviewed; saved-world/menu/crafting checks in progress.
Validator now also checks $Variable/:index tokens globally;5 existing-allocation excess warnings are informational, no fatal token/duplicate issues.
press --hold0.15 can bound real-time input; --frames depends on WebSocket broadcast timing. Never infer success from ACK alone; inspect frames.

## STEP027/028 latest checkpoint
STEP027 added278 recipe/category rows,1410 drafts/556chars; SHA256c01e42501469892f7103bc14b0f9d9e21291517488ba7ea1b4727fe68862a685.
STEP028 added491 tool/resource/action rows,1901 drafts/580chars. Some identical text recurs in legacy tables; this is not1901 unique active phrases. Nouns and actions matched in separate index ranges; ambiguous Fish verb translated by exact ID. Prior TSV snapshots retained locally under STEP026/027 (large snapshots excluded from compact package).
Both clean builds and full patch reproduction passed. STEP028 latest ISO hash above; new tools/recipes/actions still need screen review. Current owned instance is loading test save.
IMPORTANT packaging repair: packages through STEP026 used an overbroad2MB per-file filter and omitted the canonical3.3MB TSV. They are incomplete handoffs. package_handoff.py now limits only diagnostic logs, always includes translation source, and requires canonical TSV/config/modules/runner/docs/selected patch plus validates every manifest hash. Use a newly generated STEP028 package. Existing local canonical TSV was never lost.

Repaired STEP028 handoff ZIP verified: canonical16550 rows/1901 drafts present, selected patch present, all member hashes and ZIP CRC pass. Output copy is outputs/CASTAWAY_STEP028_RESULT.zip in Codex workspace. Requirements now pins the tested Pillow11.3.0; font builder safely handles no-added-glyphs and reports512-grid remaining capacity for future builds. These maintenance edits do not change STEP028 ISO.

STEP028 loaded the test save; pause and skills page Korean reviewed (step028_inventory_open.png is actually skills). Do NOT infer inventory/recipe proof from screenshot filenames. New tool/recipe/action text remains unverified.
Maintenance font build QA_FONT_028 is NOT a complete ISO candidate: font bytes exactly match STEP028 SHA256194c45eb740187b8e963ff1ab575c0f0368f5a983e4fac497ef0756d5542494f. Reported remaining512-grid slots: main11=709,title=340,main10=892,title_glow=238,main13=340. Revisit packing/font strategy before another238 distinct characters, well before full translation.
Current input testing suggests --hold0.05..0.15 depending screen; ACK is not evidence of navigation. Inspect stable text/icon selection. Leaving untranslated item QA explicit avoids false passes.

2026-10-17 checkpoint: owned STEP028 emulator inputs released and instance stopped using verified PID/start/path/port identity. Test save persists. Resume by launching configured latest build and loading that test save; no unowned process was stopped.
