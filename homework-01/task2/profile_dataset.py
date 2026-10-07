"""Task 2.2: profile the selected dataset and write a report to a file.

Re-runnable: the same input always produces an identical report.
"""
import pandas as pd

from common import (ENGLISH_CODE, HW_DIR, LABEL_FIELD, LANGUAGE_FIELD, SOURCE_COMMIT,
                    SOURCE_FILE, TEXT_FIELD, filter_english, is_missing, load_source)

REPORT_FILE = HW_DIR / "task2/profile_report.md"
SHORT_TEXT_THRESHOLD = 10   # words; justified in the report
RELEVANT_FIELDS = ["subject", TEXT_FIELD, LABEL_FIELD, "priority", "type", "answer"]
PERCENTILES = [5, 25, 50, 75, 95]
N_EXAMPLES = 5


# ---------- small helpers ----------

def pct(part: int, whole: int) -> str:
    return f"{100 * part / whole:.1f}%" if whole else "n/a"


def md_table(header: list[str], rows: list[list]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |",
             "|" + "|".join("---" for _ in header) + "|"]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return lines


def snippet(text, width: int = 80) -> str:
    """One-line, pipe-safe preview of a ticket text for Markdown tables."""
    one_line = " ".join(str(text).split()).replace("|", "\\|")
    return one_line if len(one_line) <= width else one_line[: width - 1] + "…"


def word_counts(texts: pd.Series) -> pd.Series:
    return texts.fillna("").astype(str).str.count(r"\S+")


# ---------- sections ----------

def section_overview(raw, filtered) -> list[str]:
    """Total records and columns; records after filtering; record grain."""
    lines = ["## Overview", ""]
    source_cols = [c for c in raw.columns if c != "record_id"]
    lang_present = raw[~is_missing(raw[LANGUAGE_FIELD])]

    lines += [
        f"The raw file has **{len(raw):,} rows** and **{len(source_cols)} columns** "
        f"(not counting the added `record_id`).",
        "",
        "Columns: " + ", ".join(f"`{c}`" for c in source_cols) + ".",
        "",
        "Rows remaining after each filter step:",
        "",
        *md_table(["Step", "Rows remaining", "Rows removed"], [
            ["Raw CSV", f"{len(raw):,}", "–"],
            [f"`{LANGUAGE_FIELD}` not missing", f"{len(lang_present):,}",
             f"{len(raw) - len(lang_present):,}"],
            [f"`{LANGUAGE_FIELD}` = `{ENGLISH_CODE}`", f"{len(filtered):,}",
             f"{len(lang_present) - len(filtered):,}"],
        ]),
        "",
        "Rows with a missing language are dropped because they cannot be confirmed "
        "as English. All statistics below refer to the English rows only.",
        "",
        "**Record grain:** one row represents one customer support ticket (its "
        "subject and body), together with the queue, priority and type it was "
        "assigned. There is no ticket ID, so this is inferred: the columns contain no thread, message or sequence ID that would link rows "
        "into conversations, and almost every row (all but 3 of 16,338) has its own "
        "single `answer`, so each row looks like one self-contained ticket and reply."
        "Caveat: there are no exact duplicates, but 8 near-duplicates appear after normalising (see Duplicate ticket texts).",
        "",
        "`record_id` is the 1-based row position in the raw CSV (e.g. `R00001`). It "
        "is assigned before any filtering, so the same ticket has the same ID in "
        "the 20-record sample and in this report.",
    ]
    return lines


def section_fields(filtered) -> list[str]:
    """Which columns are the ticket text and routing label, and why."""
    lines = ["## Text and label fields", ""]
    n = len(filtered)
    subj_missing = int(is_missing(filtered["subject"]).sum())
    body_missing = int(is_missing(filtered[TEXT_FIELD]).sum())

    lines += [
        f"- **Ticket text:** `{TEXT_FIELD}`, the customer's message.",
        f"- **Routing label:** `{LABEL_FIELD}`, the queue assigned to the ticket by the "
        "dataset's generator (the data is synthetic, so these are not real routing decisions). "
        "This is what a routing model would predict. `priority` and `type` are "
        "kept for context but are not the routing label.",
        "",
        f"`subject` is not used as the text field because it is missing in "
        f"{subj_missing:,} of {n:,} English rows ({pct(subj_missing, n)}), while "
        f"`{TEXT_FIELD}` is missing in {body_missing:,} ({pct(body_missing, n)}). "
        "Combining subject and body is a possible later step; it is not done here, "
        f"so every text statistic below refers to `{TEXT_FIELD}` alone.",
    ]
    return lines


def section_missing(filtered) -> list[str]:
    """Missing-value counts and proportions for the relevant fields."""
    lines = ["## Missing values", ""]
    n = len(filtered)
    rows = []
    for field in [f for f in RELEVANT_FIELDS if f in filtered.columns]:
        n_null = int(filtered[field].isna().sum())
        n_missing = int(is_missing(filtered[field]).sum())
        name = f"`{field}`" + (" (post-outcome; not a model input)" if field == "answer" else "")
        rows.append([name, f"{n_missing:,}", pct(n_missing, n),
                     f"{n_missing - n_null:,}"])

    lines += [
        "Empty strings and whitespace-only strings count as missing, in addition "
        "to true nulls. The last column shows how many of the missing values were "
        "blank strings rather than nulls.",
        "",
        *md_table(["Field", "Missing", "% of English rows", "Of which blank strings"],
                  rows),
    ]
    return lines


def section_labels(filtered) -> list[str]:
    """Routing-label counts and proportions."""
    lines = ["## Routing-label distribution", ""]
    n = len(filtered)
    labels = filtered[LABEL_FIELD].where(~is_missing(filtered[LABEL_FIELD]), "(missing)")
    counts = (labels.value_counts()
              .rename_axis("queue").reset_index(name="n")
              .sort_values(["n", "queue"], ascending=[False, True], kind="stable"))

    rows = [[f"`{r.queue}`", f"{r.n:,}", pct(r.n, n)] for r in counts.itertuples()]
    rows.append(["**Total**", f"**{n:,}**", "**100.0%**"])
    largest, smallest = counts.iloc[0], counts.iloc[-1]

    lines += [
        f"There are {len(counts)} distinct queues, sorted largest first. The largest "
        f"(`{largest.queue}`) is {largest.n / smallest.n:.1f}× the size of the "
        f"smallest (`{smallest.queue}`).",
        "",
        *md_table(["Queue", "Tickets", "% of English rows"], rows),
    ]
    return lines


def section_text_length(filtered) -> list[str]:
    """Text-length summary and suspiciously short examples."""
    lines = ["## Ticket-text length", ""]
    present = filtered[~is_missing(filtered[TEXT_FIELD])]
    n_excluded = len(filtered) - len(present)
    words = word_counts(present[TEXT_FIELD])
    chars = present[TEXT_FIELD].astype(str).str.len()

    stats = [["Min", f"{words.min():,}", f"{chars.min():,}"]]
    for p in PERCENTILES:
        stats.append([f"{p}th percentile", f"{words.quantile(p / 100):,.1f}",
                      f"{chars.quantile(p / 100):,.1f}"])
    stats += [["Max", f"{words.max():,}", f"{chars.max():,}"],
              ["Mean (for reference only)", f"{words.mean():,.1f}", f"{chars.mean():,.1f}"]]

    lines += [
        "Length is measured in **words** (whitespace-separated tokens), because "
        "word count is closer to how much information a ticket gives a person "
        "routing it. Character counts are shown alongside for reference. "
        f"{n_excluded:,} rows with a missing `{TEXT_FIELD}` are excluded here.",
        "",
        *md_table(["Statistic", "Words", "Characters"], stats),
        "",
    ]

    short = (present.assign(n_words=words)
             .loc[lambda d: d["n_words"] < SHORT_TEXT_THRESHOLD]
             .sort_values(["n_words", "record_id"], kind="stable"))
    lines += [
        f"**Suspiciously short texts:** {len(short):,} tickets "
        f"({pct(len(short), len(present))}) have fewer than {SHORT_TEXT_THRESHOLD} "
        f"words, so the threshold flags roughly the shortest {pct(len(short), len(present))} "
        "of tickets. Of the 5 shortest examples, 4 (R07608, R00872, R01104, R01548) cannot be "
        "routed: they contain no product or problem. The fifth (R25288) is a full "
        "sentence with its spaces removed, so it is a formatting defect rather than a "
        "short ticket, and word counts undercount texts like it.",
        "",
    ]
    if short.empty:
        lines.append("None found.")
    else:
        lines.append(f"The {min(N_EXAMPLES, len(short))} shortest:")
        lines.append("")
        lines += md_table(["record_id", "Words", "Queue", "Text"], [
            [r.record_id, r.n_words, getattr(r, LABEL_FIELD), snippet(getattr(r, TEXT_FIELD))]
            for r in short.head(N_EXAMPLES).itertuples()
        ])
    return lines


def section_duplicates(filtered) -> list[str]:
    """Exact duplicate ticket texts."""
    lines = ["## Duplicate ticket texts", ""]
    present = filtered[~is_missing(filtered[TEXT_FIELD])]
    text = present[TEXT_FIELD]

    in_group = text.duplicated(keep=False)          # every row that has a twin
    extra = int(text.duplicated(keep="first").sum())  # copies beyond the first
    n_groups = int(text[in_group].nunique())

    normalised = text.astype(str).str.lower().str.split().str.join(" ")
    norm_extra = int(normalised.duplicated(keep="first").sum())
    norm_groups = int(normalised[normalised.duplicated(keep=False)].nunique())

    groups = (present[in_group]
              .groupby(TEXT_FIELD, sort=False)
              .agg(ids=("record_id", lambda s: ", ".join(sorted(s))),
                   size=("record_id", "size"),
                   n_queues=(LABEL_FIELD, lambda s: s.nunique(dropna=False)))
              .reset_index()
              .sort_values(["size", "ids"], ascending=[False, True], kind="stable"))
    conflicting = int((groups["n_queues"] > 1).sum())

    lines += [
        f"\"Exact\" means the `{TEXT_FIELD}` values are identical character for "
        "character (no trimming, case-folding or whitespace changes). Rows with a "
        "missing text are excluded.",
        "",
        f"- Rows whose text exactly duplicates another row's: **{int(in_group.sum()):,}**, "
        f"in {n_groups:,} groups.",
        f"- Redundant copies (rows that would be removed if only the first of each "
        f"group were kept): **{extra:,}**.",
        f"- Duplicate groups whose rows have different queues: **{conflicting:,}**. "
        "These are label conflicts: the same text was assigned different queues.",
        "",
                "Reported separately, and **not** part of the exact count: after "
        "normalising (lower-casing and collapsing whitespace) there are "
        f"{norm_extra:,} redundant copies in {norm_groups:,} groups. "
        "This differs from the Task 1 check, which removed whitespace entirely "
        "and covered all languages, so the two counts are not directly comparable.",
        "",
    ]
    if groups.empty:
        lines.append("No exact duplicate groups found.")
    else:
        lines.append(f"The {min(N_EXAMPLES, len(groups))} largest groups:")
        lines.append("")
        lines += md_table(["Rows", "record_ids", "Same queue?", "Text"], [
            [r.size, r.ids, "yes" if r.n_queues == 1 else "no", snippet(getattr(r, TEXT_FIELD))]
            for r in groups.head(N_EXAMPLES).itertuples()
        ])
    return lines


def main() -> None:
    raw = load_source()
    filtered = filter_english(raw)

    lines = [
        "# Profile report: selected support-ticket dataset",
        f"Source: `{SOURCE_FILE.name}` (commit `{SOURCE_COMMIT}`)",
        "",
    ]
    for section in (
        section_overview(raw, filtered),
        section_fields(filtered),
        section_missing(filtered),
        section_labels(filtered),
        section_text_length(filtered),
        section_duplicates(filtered),
    ):
        lines += section + [""]

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT_FILE}")


if __name__ == "__main__":
    main()
