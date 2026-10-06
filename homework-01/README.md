# Homework 1: Acquire, Inspect, and Augment

## Setup

- Python 3.14.7 (as pinned by the assignment); dependencies pinned in `requirements.txt` (`pandas==3.0.5`)
- Create and activate the virtual environment, then install the pinned dependencies (Git Bash on Windows):
  ```bash
  py -3.14 -m venv .venv
  source .venv/Scripts/activate
  python -m pip install -r requirements.txt
  python --version   # expect 3.14.7
  ```
  On macOS/Linux use `python3.14 -m venv .venv` and `source .venv/bin/activate`.
- Run all scripts from `homework-01/`, e.g. `python task1/inspect_kaggle.py`

## Data

Raw files live in `data/raw/` and are **not committed**. Download them as below, then check
each file against its SHA-256 (`sha256sum <file>`).

### Selected dataset

- **Name:** Customer Support Tickets (Tobi-Bueck)
- **Source:** https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets
- **DOI:** 10.57967/hf/6184
- **File:** `aa_dataset-tickets-multi-lang-5-2-50-version.csv`
- **Commit:** `ddf1c81a5475992c4fa6752bf1e8b4e31f07bbeb` (repo last modified 2026-06-28)
- **Retrieved:** 2026-09-30
- **SHA-256:** `f187c090e59581c2bbf3aa1377c8db4dd647464ecf2ae51bf8966e42e0ed6bc0`
- **License:** CC-BY-NC-4.0 (non-commercial use; attribution required)
- **Place at:** `data/raw/tobi-bueck/aa_dataset-tickets-multi-lang-5-2-50-version.csv`

### Other files used as Task 1 evidence

`task1/compare_files.py`, `task1/overlap_check.py` and `task1/inspect_kaggle.py` also read these:

| Dataset | File | Version | Retrieved | Place at | SHA-256 |
|---|---|---|---|---|---|
| [Tobi-Bueck](https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets) (older release) | `dataset-tickets-multi-lang-4-20k.csv` | commit `ddf1c81…` | 2026-09-30 | `data/raw/tobi-bueck/` | `9be3bf810584fe01e8e83383e83dfd33f4c3910938ecad03ef151da79d8f0635` |
| [IT Support Ticket Data (parthpatil256)](https://www.kaggle.com/datasets/parthpatil256/it-support-ticket-data) | `IT Support Ticket Data.csv` | Kaggle v1 (2025-06-14) | 2026-09-30 | `data/raw/parthpatil256/` | `a71c434ad7da3cd033b9dc9cd777d4e1ce7d1f1c8959a92b7a7ed54213e9677a` |
| [Synthetic IT Support Tickets (alexandermeau)](https://www.kaggle.com/datasets/alexandermeau/synthetic-it-support-tickets) | `itsm_ticket_corpus_flat.csv` | Kaggle v13 (2026-06-15) | 2026-09-30 | `data/raw/alexandermeau/` | `2e3447d1e8daa1cabf1af967c0e53537c012686ea4368ffa767353d46cce8f35` |

### Download

Hugging Face files (commit-pinned, so the bytes match the checksums above):

```bash
mkdir -p data/raw/tobi-bueck
BASE="https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets/resolve/ddf1c81a5475992c4fa6752bf1e8b4e31f07bbeb"
curl -L -o data/raw/tobi-bueck/aa_dataset-tickets-multi-lang-5-2-50-version.csv "$BASE/aa_dataset-tickets-multi-lang-5-2-50-version.csv"
curl -L -o data/raw/tobi-bueck/dataset-tickets-multi-lang-4-20k.csv "$BASE/dataset-tickets-multi-lang-4-20k.csv"
```

Kaggle files: Kaggle has no commit-pinned URLs and requires a login. Download each dataset
from its page (**Download** button), extract the zip into the "Place at" folder above, and
confirm the SHA-256. If Kaggle has published a newer version, the checksum will not match and
results may differ.

## Structure

- `task1/`: candidate comparison table, provenance and overlap checks (`compare_files.py`, `overlap_check.py`, `inspect_kaggle.py`), dataset selection
- `task2/`: 20-record inspection notes, profiling script and saved profile report
- `task3/`: augmentation plan, deterministic synthetic-data generator, 50 generated records, inspection notes
