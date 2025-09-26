#!/usr/bin/env python3
"""
benchmark_updater.py  (v2)

Enhancements:
- Accept multiple --from-notes and multiple --from-json in a single run.
- Optional Excel export via --xlsx path (requires pandas + openpyxl).

Append ChestX-ray14 benchmark entries to a master CSV (and optional Markdown/Excel),
parsing either:
  A) JSON (list[dict]) with well-known keys, or
  B) Simple "Key: Value" notes (one paper per block), tolerant to naming variants.

FIELDS (canonical)
------------------
- paper_year (str): e.g., "CheXNet (2017)"
- model (str): e.g., "DenseNet-121"
- input_resolution (str): e.g., "384x384" or "384×384"
- loss (str): e.g., "Weighted BCE"
- optimizer (str): e.g., "AdamW"
- epochs (str|int): e.g., "30"
- reported_auc (str): e.g., "0.89" or "Avg AUC 0.89"
- reported_f1 (str): e.g., "0.61"
- interpretability (str): e.g., "Grad-CAM++"
- notes (str)

USAGE
-----
Examples:
1) Merge two notes files and one json file, write CSV + MD + XLSX:
   python benchmark_updater.py \
      --csv chestx_benchmarks.csv \
      --from-notes notes1.txt --from-notes notes2.txt \
      --from-json summaries.json \
      --md chestx_benchmarks.md \
      --xlsx chestx_benchmarks.xlsx

2) JSON shape (list of dicts):
    [
      {"paper_year": "Example 2023", "model": "EfficientNet-B4", ...}
    ]
"""
import argparse
import csv
import json
import re
from pathlib import Path
from typing import List, Dict, Any

CANONICAL_FIELDS = [
    "paper_year",
    "model",
    "input_resolution",
    "loss",
    "optimizer",
    "epochs",
    "reported_auc",
    "reported_f1",
    "interpretability",
    "notes",
]

# Map many key name variants to our canonical names.
KEY_ALIASES = {
    "paper & year": "paper_year",
    "paper": "paper_year",
    "year": "paper_year",
    "model backbone": "model",
    "backbone": "model",
    "architecture": "model",
    "input": "input_resolution",
    "resolution": "input_resolution",
    "input size": "input_resolution",
    "input resolution": "input_resolution",
    "loss": "loss",
    "loss function": "loss",
    "optimizer": "optimizer",
    "epochs": "epochs",
    "reported auc": "reported_auc",
    "auc": "reported_auc",
    "reported f1": "reported_f1",
    "f1": "reported_f1",
    "interpretability (grad-cam, attention, etc.)": "interpretability",
    "interpretability": "interpretability",
    "notes": "notes",
}

def canonicalize_key(k: str) -> str:
    k = (k or "").strip().lower()
    return KEY_ALIASES.get(k, k.replace(" ", "_"))

def normalize_entry(d: Dict[str, Any]) -> Dict[str, str]:
    out = {k: "" for k in CANONICAL_FIELDS}
    for k, v in d.items():
        ck = canonicalize_key(k)
        if ck in out:
            out[ck] = "" if v is None else str(v).strip()
    # Basic cleanup of resolution: unify "×" and "x"
    if out["input_resolution"]:
        out["input_resolution"] = out["input_resolution"].replace("×", "x").replace("X", "x")
    return out

def parse_notes_blocks(text: str) -> List[Dict[str, str]]:
    blocks = re.split(r"\n\s*\n", text.strip(), flags=re.MULTILINE)
    entries = []
    for b in blocks:
        data = {}
        for line in b.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
        if data:
            entries.append(normalize_entry(data))
    return entries

def read_json(path: Path) -> List[Dict[str, str]]:
    items = json.loads(path.read_text(encoding="utf-8"))
    out = []
    if isinstance(items, dict):
        items = [items]
    for it in items:
        out.append(normalize_entry(it))
    return out

def load_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append({k: row.get(k, "") for k in CANONICAL_FIELDS})
    return rows

def save_csv(path: Path, rows: List[Dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CANONICAL_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def save_xlsx(path: Path, rows: List[Dict[str, str]]) -> None:
    try:
        import pandas as pd
        df = pd.DataFrame(rows, columns=CANONICAL_FIELDS)
        df.to_excel(path, index=False)
    except Exception as e:
        print(f"Warning: Could not write Excel file '{path}': {e}")

def dedupe(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen = set()
    out = []
    for r in rows:
        key = (r.get("paper_year","").lower(), r.get("model","").lower())
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out

def to_markdown(rows: List[Dict[str, str]]) -> str:
    header = (
        "| Paper & Year | Model Backbone | Input Resolution | Loss Function | Optimizer | Epochs | "
        "Reported AUC | Reported F1 | Interpretability | Notes |\n"
        "|--------------|----------------|------------------|---------------|-----------|--------|"
        "--------------|-------------|------------------|-------|\n"
    )
    lines = [header]
    for r in rows:
        lines.append(
            f"| {r['paper_year'] or ''} | {r['model'] or ''} | {r['input_resolution'] or ''} | "
            f"{r['loss'] or ''} | {r['optimizer'] or ''} | {r['epochs'] or ''} | "
            f"{r['reported_auc'] or ''} | {r['reported_f1'] or ''} | "
            f"{r['interpretability'] or ''} | {r['notes'] or ''} |"
        )
        lines.append("\n")
    return "".join(lines)

def main():
    ap = argparse.ArgumentParser(description="Append ChestX-ray14 benchmark entries to a CSV (and optional Markdown/Excel).")
    ap.add_argument("--csv", required=True, help="Path to CSV file to create/update.")
    ap.add_argument("--from-json", action="append", help="Path to JSON file with list[dict] entries. Can be repeated.", default=[])
    ap.add_argument("--from-notes", action="append", help="Path to plaintext notes with 'Key: Value' blocks. Can be repeated.", default=[])
    ap.add_argument("--md", help="Optional path to write Markdown table.")
    ap.add_argument("--xlsx", help="Optional path to write Excel (.xlsx).")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    rows = load_csv(csv_path)

    new_entries: List[Dict[str, str]] = []
    for j in args.from_json:
        new_entries.extend(read_json(Path(j)))
    for n in args.from_notes:
        notes_text = Path(n).read_text(encoding="utf-8")
        new_entries.extend(parse_notes_blocks(notes_text))

    if not new_entries:
        print("No new entries provided. Use --from-json or --from-notes.")
        return

    rows.extend(new_entries)
    rows = dedupe(rows)

    # Optional: sort by reported_auc (descending) then reported_f1 (descending) when numeric
    def maybe_float(x: str):
        try:
            import math, re
            num = re.findall(r"[0-9]*\.?[0-9]+", x)[0] if x else ""
            return float(num) if num != "" else math.nan
        except Exception:
            import math
            return math.nan

    rows.sort(key=lambda r: (maybe_float(r.get("reported_auc","")), maybe_float(r.get("reported_f1",""))), reverse=True)

    save_csv(csv_path, rows)
    print(f"Saved CSV with {len(rows)} rows to {csv_path}")

    if args.md:
        md_text = to_markdown(rows)
        Path(args.md).write_text(md_text, encoding="utf-8")
        print(f"Wrote Markdown table to {args.md}")

    if args.xlsx:
        save_xlsx(Path(args.xlsx), rows)
        print(f"Wrote Excel file to {args.xlsx}")

if __name__ == "__main__":
    main()
