"""Task 3 prep: find candidate seed tickets by vocabulary, not just by label.

Random samples showed that most tickets labelled with a small queue are not
about that queue's topic (HR: 3 of 40; Returns and Exchanges: 3 of 40). So this
script narrows the queue to tickets whose subject or body uses the queue's own
vocabulary, then saves them for hand review. The keyword filter only shortlists:
every seed is still read and approved by hand.

Usage:  python task3/find_seeds.py
"""
import sys
from pathlib import Path

TASK2_DIR = Path(__file__).resolve().parent.parent / "task2"
sys.path.insert(0, str(TASK2_DIR))

from common import HW_DIR, LABEL_FIELD, TEXT_FIELD, filter_english, load_source  # noqa: E402

TARGET_QUEUE = "Returns and Exchanges"
KEYWORDS = (r"\b(?:return(?:s|ed|ing)?|refund(?:s|ed)?|exchang(?:e|es|ed|ing)|"
            r"replace(?:ment|d)?|swap(?:ped)?|rma|send (?:it )?back|sent back|"
            r"defective|faulty|damaged|wrong item|warranty)\b")
OUT_FILE = HW_DIR / "task3/returns_seed_candidates.csv"


def main() -> None:
    df = filter_english(load_source())
    text = (df["subject"].fillna("") + " " + df[TEXT_FIELD].fillna("")).str.lower()
    hit = text.str.contains(KEYWORDS, regex=True)

    # How the returns vocabulary is spread across queues (evidence for the plan).
    print("Tickets using returns vocabulary, by queue:")
    by_queue = df[hit][LABEL_FIELD].value_counts()
    totals = df[LABEL_FIELD].value_counts()
    for queue, n in by_queue.items():
        print(f"  {queue:<35} {n:>5} of {totals[queue]:>5} ({100 * n / totals[queue]:.1f}%)")

    in_queue = df[hit & (df[LABEL_FIELD] == TARGET_QUEUE)].copy()
    in_queue["n_words"] = in_queue[TEXT_FIELD].fillna("").str.split().str.len()
    cols = ["record_id", "subject", TEXT_FIELD, "priority", "type", "n_words"]
    in_queue.sort_values("record_id")[cols].to_csv(OUT_FILE, index=False)
    print(f"\nSaved {len(in_queue)} '{TARGET_QUEUE}' tickets that use returns "
          f"vocabulary (of {totals[TARGET_QUEUE]}) to {OUT_FILE}")


if __name__ == "__main__":
    main()
