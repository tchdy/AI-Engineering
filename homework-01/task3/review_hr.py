"""Task 3 prep: dump a seeded random set of English tickets from one queue for hand review.

Usage:  python task3/review_hr.py                          (Human Resources)
        python task3/review_hr.py "Returns and Exchanges"  (any other queue)

Read the output, mark which tickets clearly belong to the queue and are cleanly
written, and use only those as seed records for the generator.
"""
import sys
from pathlib import Path

TASK2_DIR = Path(__file__).resolve().parent.parent / "task2"
sys.path.insert(0, str(TASK2_DIR))          # reuse Task 2's loading and record_ids

from common import HW_DIR, LABEL_FIELD, TEXT_FIELD, filter_english, load_source  # noqa: E402

TARGET_QUEUE = sys.argv[1] if len(sys.argv) > 1 else "Human Resources"
SEED = 42
N_REVIEW = 40
_SLUG = {"Human Resources": "hr"}.get(
    TARGET_QUEUE, TARGET_QUEUE.lower().replace(" and ", "_").replace(" ", "_").replace("-", "_"))
OUT_FILE = HW_DIR / f"task3/{_SLUG}_candidates.csv"


def main() -> None:
    df = filter_english(load_source())
    hr = df[df[LABEL_FIELD] == TARGET_QUEUE]
    sample = (hr.sample(min(N_REVIEW, len(hr)), random_state=SEED)
                .sort_values("record_id"))
    sample = sample.assign(n_words=sample[TEXT_FIELD].fillna("").str.split().str.len())

    cols = ["record_id", "subject", TEXT_FIELD, "priority", "type", "n_words"]
    sample[cols].to_csv(OUT_FILE, index=False)
    print(f"{len(hr)} English '{TARGET_QUEUE}' tickets; "
          f"saved {len(sample)} (seed {SEED}) to {OUT_FILE}")


if __name__ == "__main__":
    main()
