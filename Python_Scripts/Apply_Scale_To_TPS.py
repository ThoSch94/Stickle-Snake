#!/usr/bin/env python3
"""Apply scale values from a CSV to TPS landmark blocks.

Usage:
  python Apply_Scale_To_TPS.py --csv scales.csv --tps input.tps --out output.tps

CSV must have columns: specimen,scale (column names configurable)
TPS file is parsed into blocks starting with a line beginning `LM=`. For each block
the script finds `IMAGE=` (or `ID=`) to match the specimen and inserts a line
`SCALE=<value>` immediately after the `VARIABLES=` line in that block. If no
`VARIABLES=` line exists, `SCALE=` is appended at the end of the block.
"""

import argparse
import csv
import os
import sys
from typing import Dict, List, Optional


def read_scale_csv(path: str, specimen_col: str, scale_col: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get(specimen_col)
            val = row.get(scale_col)
            if key and val:
                mapping[key.strip()] = val.strip()
    return mapping


def split_blocks(lines: List[str]) -> List[List[str]]:
    blocks: List[List[str]] = []
    current: List[str] = []
    for line in lines:
        # Start a new block when encountering an LM= line and current not empty
        if line.startswith('LM=') and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks


def basename_without_ext(path: str) -> str:
    base = os.path.basename(path)
    if '.' in base:
        return '.'.join(base.split('.')[:-1])
    return base


def find_image_or_id(block: List[str]) -> Optional[str]:
    for line in block:
        if line.startswith('IMAGE='):
            return line.split('=', 1)[1].strip()
    for line in block:
        if line.startswith('ID='):
            return line.split('=', 1)[1].strip()
    return None


def normalize_name(name: str) -> str:
    # Remove extension if present, remove common suffixes like _mirrored
    n = basename_without_ext(name)
    # drop trailing common suffixes
    for suf in ('_mirrored', '_mirror', '_rotated'):
        if n.endswith(suf):
            n = n[: -len(suf)]
    return n


def match_scale(mapping: Dict[str, str], image_name: str) -> Optional[str]:
    if not image_name:
        return None
    img = normalize_name(image_name)
    # exact match
    if img in mapping:
        return mapping[img]
    # try keys after stripping leading 0_ or 0__
    img_no_lead = img.lstrip('0_')
    if img_no_lead in mapping:
        return mapping[img_no_lead]
    # try substring matches both ways
    for k in mapping:
        if k in img or img in k:
            return mapping[k]
    # try relaxed by removing any leading numeric token and underscore
    parts = img.split('_')
    if len(parts) > 1:
        alt = '_'.join(parts[1:])
        if alt in mapping:
            return mapping[alt]
    return None


def insert_scale_into_block(block: List[str], scale: str) -> List[str]:
    out: List[str] = []
    inserted = False
    for i, line in enumerate(block):
        out.append(line)
        if not inserted and line.startswith('VARIABLES='):
            out.append(f'SCALE={scale}')
            inserted = True
    if not inserted:
        # append at the end of the block
        out.append(f'SCALE={scale}')
    return out


def process_tps(input_path: str, output_path: str, mapping: Dict[str, str]) -> None:
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = [ln.rstrip('\n') for ln in f]

    blocks = split_blocks(lines)

    matched = 0
    unmatched_blocks: List[int] = []
    new_lines: List[str] = []

    for idx, block in enumerate(blocks):
        image_or_id = find_image_or_id(block)
        scale = match_scale(mapping, image_or_id) if image_or_id else None
        if scale is not None:
            new_block = insert_scale_into_block(block, scale)
            matched += 1
        else:
            new_block = block
            unmatched_blocks.append(idx + 1)
        new_lines.extend(new_block)

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        for ln in new_lines:
            f.write(ln + '\n')

    print(f'Wrote {output_path}. Matched: {matched}. Unmatched blocks: {len(unmatched_blocks)}')
    if unmatched_blocks:
        print('Unmatched block indices (1-based):', unmatched_blocks)


def main(argv=None):
    p = argparse.ArgumentParser(description='Apply scales from CSV to TPS blocks')
    p.add_argument('--csv', required=True, help='CSV path with specimen->scale mapping')
    p.add_argument('--tps', required=True, help='Input TPS file')
    p.add_argument('--out', required=True, help='Output TPS file to write')
    p.add_argument('--specimen-col', default='specimen', help='CSV specimen column name')
    p.add_argument('--scale-col', default='scale_mm_per_pix', help='CSV scale column name')
    args = p.parse_args(argv)

    mapping = read_scale_csv(args.csv, args.specimen_col, args.scale_col)
    if not mapping:
        print('No mappings read from CSV; check column names and file.', file=sys.stderr)
        sys.exit(2)

    process_tps(args.tps, args.out, mapping)


if __name__ == '__main__':
    main()