"""Task 2.1: select 20 source records reproducibly and save them for inspection."""
import pandas as pd

from common import HW_DIR, LABEL_FIELD, TEXT_FIELD, filter_english, is_missing, load_source

SEED = 42          # DECISION: record this in your notes
N = 20
OUT_FILE = HW_DIR / "task2/sample_20.csv"
OUT_COLUMNS = ["record_id", "selection_method", "subject", TEXT_FIELD,
               LABEL_FIELD, "priority", "type"]

# DECISION: a random core plus a few targeted picks (Lesson 2, slides 21-27).
#   - Up to 4 targeted picks cover edge cases that 20 random rows would likely
#     miss: the shortest text, a missing subject, an exact duplicate text, and
#     the rarest queue.
#   - The remaining rows are a plain random sample (seed 42) of everything
#     else, so they give an unbiased view of a "typical" ticket.
#   - The `selection_method` column records which method chose each row.
#     Only the random rows should be used to judge how common something is.


def targeted_picks(df: pd.DataFrame) -> dict[str, str]:
    """Return {record_id: method} for the targeted picks (deterministic)."""
    picks: dict[str, str] = {}
    text = df[TEXT_FIELD]

    # 1. Shortest non-empty ticket text, ties broken by record_id.
    shortest = (df[~is_missing(text)]
                .assign(n_words=text.fillna("").astype(str).str.split().str.len())
                .sort_values(["n_words", "record_id"], kind="stable"))
    picks[shortest["record_id"].iloc[0]] = "targeted: shortest text"

    def take_random(candidates: pd.DataFrame, method: str) -> None:
        candidates = candidates[~candidates["record_id"].isin(list(picks))]
        if not candidates.empty:
            chosen = candidates.sample(1, random_state=SEED)["record_id"].iloc[0]
            picks[chosen] = method

    # 2. A ticket with a missing subject.
    take_random(df[is_missing(df["subject"])], "targeted: missing subject")

    # 3. A ticket whose text exactly duplicates another ticket's text.
    take_random(df[~is_missing(text) & text.duplicated(keep=False)],
                "targeted: exact duplicate text")

    # 4. A ticket from the rarest queue (alphabetical tie-break).
    counts = df[LABEL_FIELD].value_counts()
    rarest = sorted(counts[counts == counts.min()].index)[0]
    take_random(df[df[LABEL_FIELD] == rarest], f"targeted: rarest queue ({rarest})")

    return picks


def main() -> None:
    df = filter_english(load_source())

    picks = targeted_picks(df)
    targeted = df[df["record_id"].isin(list(picks))]
    rest = df[~df["record_id"].isin(list(picks))]
    random_core = rest.sample(N - len(picks), random_state=SEED)

    sample = pd.concat([targeted, random_core])
    sample["selection_method"] = sample["record_id"].map(picks).fillna("random")
    sample = sample.sort_values("record_id")[OUT_COLUMNS]

    sample.to_csv(OUT_FILE, index=False)
    print(f"Saved {len(sample)} records ({len(targeted)} targeted, "
          f"{len(random_core)} random, seed {SEED}) to {OUT_FILE}")


if __name__ == "__main__":
    main()
