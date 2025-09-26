# Research Tools: ChestX-ray14 Benchmarking

This folder contains scripts and data pipelines for tracking, updating, and comparing 
PyTorch models benchmarked on the NIH ChestX-ray14 dataset.

---

## 📂 Folder Structure
.
├── data
│   └── chestx_benchmarks.csv
├── outputs
│   ├── chestx_benchmarks.md
│   └── chestx_benchmarks.xlsx
├── README.md
└── scripts
    └── benchmark_updater


---

## 🚀 Usage

### Update Benchmarks from Notes
1. Collect notes from Claude/Perplexity in `notes.txt` using `Key: Value` format.
2. Run:
```bash
cd ~/Dropbox/machine_learning/research_tools
python3 scripts/benchmark_updater.py \
  --csv data/chestx_benchmarks.csv \
  --from-notes notes.txt \
  --md outputs/chestx_benchmarks.md \
  --xlsx outputs/chestx_benchmarks.xlsx

# Update from JSON
python3 scripts/benchmark_updater.py \
  --csv data/chestx_benchmarks.csv \
  --from-json summaries.json \
  --md outputs/chestx_benchmarks.md \
  --xlsx outputs/chestx_benchmarks.xlsx

# Merge Multiple Sources
python3 scripts/benchmark_updater.py \
  --csv data/chestx_benchmarks.csv \
  --from-notes notes1.txt --from-notes notes2.txt \
  --from-json summaries.json \
  --md outputs/chestx_benchmarks.md \
  --xlsx outputs/chestx_benchmarks.xlsx
