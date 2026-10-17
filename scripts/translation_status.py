"""Report source coverage without mistaking blank/debug rows for game completion."""
import argparse, collections, csv, datetime, json, re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--output', type=Path, default=root / 'translation/status.json')
a = p.parse_args()
with (root / 'translation/text_master.tsv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f, delimiter='\t'))
counts = collections.Counter()
resources = collections.defaultdict(collections.Counter)
pending = []
for r in rows:
    source = r['source_text'].strip()
    if r.get('category') in ('KeyboardCharacter', 'FontCharacterCoverage'):
        bucket = 'character_data_preserved'
    elif r.get('category') == 'TechnicalLiteral':
        bucket = 'technical_literal_preserved'
    elif r['ko_current']:
        bucket = 'translated_draft'
    elif not source:
        bucket = 'blank_preserved'
    elif not re.search(r'[A-Za-z\uac00-\ud7a3]', re.sub(r'<[^>]*>', '', source)):
        bucket = 'symbol_or_markup_preserved'
    elif re.match(r'(?i)^(?:DEBUG\b|D - |Debug\.\.\.)', source):
        bucket = 'debug_pending'
    elif re.match(r'(?i)^(?:\[?TEMP\b|OBSOLETE\b|unused\b)', source):
        bucket = 'temp_or_legacy_pending_usage_unconfirmed'
    else:
        bucket = 'text_pending'
    counts[bucket] += 1
    resources[r['resource_id']][bucket] += 1
    if bucket.endswith('pending') or bucket.endswith('unconfirmed'):
        pending.append({'id': r['id'], 'resource_id': r['resource_id'], 'string_index': r['string_index'], 'classification': bucket, 'source_text': r['source_text']})
with (root / 'translation/supplemental_text.tsv').open(encoding='utf-8-sig', newline='') as f:
    supplemental = list(csv.DictReader(f, delimiter='\t'))
with (root / 'translation/image_manifest.tsv').open(encoding='utf-8-sig', newline='') as f:
    images = list(csv.DictReader(f, delimiter='\t'))
report = {'updated': datetime.datetime.now().astimezone().isoformat(), 'rows': len(rows), 'counts': dict(counts), 'resources': {k: dict(v) for k, v in resources.items()}, 'required_non_ascii_characters': len({c for r in rows + supplemental for c in r['ko_current'] if ord(c) > 127}), 'supplemental_drafts': sum(bool(r['ko_current']) for r in supplemental), 'movie_caption_drafts': 1, 'identified_text_first_draft_complete': not pending and all(r['ko_current'] for r in supplemental), 'image_decisions': dict(collections.Counter(r['translation_status'] for r in images)), 'all_assets_translated': False, 'runtime': 'NOT_TESTED_USER_OWNS_QA', 'note': 'All identified linguistic rows have drafts; blank/character/symbol/technical literals are preserved. This is not active-screen coverage or runtime verification. Scope and limitations: ASSET_SCOPE_083.md.'}
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
with (root / 'translation/pending_text.tsv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, ['id', 'resource_id', 'string_index', 'classification', 'source_text'], delimiter='\t')
    w.writeheader()
    w.writerows(pending)
print(json.dumps(report, ensure_ascii=True))
