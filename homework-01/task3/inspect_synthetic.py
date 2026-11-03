"""Task 3.3: choose 10 generated records to inspect.

- 5 are drawn at random (seeded), so they represent a typical generated record.
- For the other 5, this script prints simple warning signals for every record
  (near-duplicates, grammar slips, mixed voice, length). I then pick the 5 most
  suspicious by hand from that list. The script only helps me find them.

Usage:  python task3/inspect_synthetic.py
"""
import random
import re
from pathlib import Path

import pandas as pd

HW_DIR = Path(__file__).resolve().parent.parent
IN_FILE = HW_DIR / "task3/synthetic_returns_50.csv"
INSPECT_SEED = 7
N_RANDOM = 5


def words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9'-]+", text.lower()))


def main() -> None:
    df = pd.read_csv(IN_FILE)
    ids = list(df["record_id"])
    random_pick = sorted(random.Random(INSPECT_SEED).sample(ids, N_RANDOM))
    print("Random picks (seed {}): {}\n".format(INSPECT_SEED, ", ".join(random_pick)))

    bodies = dict(zip(df["record_id"], df["body"]))
    vocab = {rid: words(b) for rid, b in bodies.items()}

    rows = []
    for r in df.itertuples():
        # Most similar other record (Jaccard similarity of word sets).
        sims = [(len(vocab[r.record_id] & vocab[o]) / len(vocab[r.record_id] | vocab[o]), o)
                for o in ids if o != r.record_id]
        best_sim, twin = max(sims)
        text = f"{r.subject} {r.body}"
        flags = []
        if re.search(r"\ba [aeiouAEIOU]", text):
            flags.append("a/an")
        if re.search(r"\bUsb\b", r.subject):
            flags.append("title-case")
        if re.search(r"\bwe\b|\bour\b|\bus\b", r.body, re.I) and re.search(r"\bI\b|\bme\b", r.body):
            flags.append("mixed voice")
        if re.search(r"(them|several|and) .*\bfound that it\b", r.body):
            flags.append("plural/it")
        rows.append({"record_id": r.record_id, "scenario": r.scenario, "words": len(r.body.split()),
                     "most_similar": twin, "similarity": round(best_sim, 2),
                     "flags": ", ".join(flags), "random": r.record_id in random_pick})

    report = pd.DataFrame(rows).sort_values(["similarity", "record_id"], ascending=[False, True])
    with pd.option_context("display.width", 140, "display.max_rows", 100):
        print(report.to_string(index=False))


if __name__ == "__main__":
    main()
