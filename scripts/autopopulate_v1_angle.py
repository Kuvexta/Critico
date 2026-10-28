"""Derive v1_angle from the rubric's dimension mapping. Preserve existing nonempty manual values, ignore unmapped dimensions and return the sorted union. Without --in-place, write the resulting record to stdout."""
from __future__ import annotations
import sys
from pathlib import Path
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from critic_i18n import translate, configure_arguments, LocalizedArgumentParser
import argparse
import json
import sys
from pathlib import Path
import yaml

def load_rubric(path: str) -> dict[int, list[int]]:
    r = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    mapping: dict[int, list[int]] = {}
    for d in r.get('dimensions', []):
        mapping[int(d['id'])] = [int(v) for v in d.get('v1', [])]
    return mapping

def derive_v1_angle(dimensions: list[str | int], mapping: dict[int, list[int]]) -> list[int]:
    angles: set[int] = set()
    for dim in dimensions:
        try:
            did = int(dim)
        except (TypeError, ValueError):
            continue
        angles.update(mapping.get(did, []))
    return sorted(angles)

def process_record(rec: dict, mapping: dict[int, list[int]]) -> dict:
    existing = rec.get('v1_angle')
    if isinstance(existing, list) and existing:
        return rec
    dims = rec.get('dimension') or rec.get('dimensions') or []
    derived = derive_v1_angle(dims, mapping)
    if derived:
        rec['v1_angle'] = derived
    return rec

def main() -> None:
    arguments = configure_arguments()
    ap = LocalizedArgumentParser(description=translate('autopopulate_v1_angle.4ad132fd6bc1'))
    ap.add_argument('rubric', help=translate('autopopulate_v1_angle.8df5fd9b986f'))
    ap.add_argument('input', help=translate('autopopulate_v1_angle.b3c3073b38fe'))
    ap.add_argument('--in-place', action='store_true', help=translate('autopopulate_v1_angle.0e9f39410a8c'))
    args = ap.parse_args(arguments)
    mapping = load_rubric(args.rubric)
    src = Path(args.input)
    text = src.read_text(encoding='utf-8')
    if src.suffix == '.jsonl':
        records = [json.loads(line) for line in text.splitlines() if line.strip()]
        out_records = [process_record(r, mapping) for r in records]
        output = '\n'.join((json.dumps(r, ensure_ascii=False) for r in out_records)) + '\n'
    else:
        rec = yaml.safe_load(text)
        out_rec = process_record(rec, mapping)
        output = yaml.safe_dump(out_rec, sort_keys=False, allow_unicode=True, width=120)
    if args.in_place:
        src.write_text(output, encoding='utf-8')
        print(translate('autopopulate_v1_angle.b602643889d2', v0=src))
    else:
        sys.stdout.write(output)
if __name__ == '__main__':
    main()
