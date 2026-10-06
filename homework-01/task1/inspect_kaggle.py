"""Task 1: inspect the two Kaggle candidates.

Run from homework-01/:
    python task1/inspect_kaggle.py

Prints, for each dataset: shape, columns and label counts.
For parthpatil256: how many normalised bodies also appear in Tobi-Bueck v5.
"""
import json
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
TOBI_V5 = RAW / "tobi-bueck" / "aa_dataset-tickets-multi-lang-5-2-50-version.csv"
TOBI_V4 = RAW / "tobi-bueck" / "dataset-tickets-multi-lang-4-20k.csv"
ALEX = RAW / "alexandermeau" / "itsm_ticket_corpus_flat.csv"

# parthpatil256: find the single CSV in its folder, so the script doesn't
# depend on guessing the file name inside the Kaggle zip.
parth_files = sorted((RAW / "parthpatil256").glob("*.csv"))
if len(parth_files) != 1:
    raise SystemExit(f"Expected exactly one CSV in data/raw/parthpatil256/, found: {parth_files}")
PARTH = parth_files[0]


def normalise(s: pd.Series) -> pd.Series:
    """Lowercase and remove ALL whitespace (spaces, tabs, newlines). Missing -> empty.

    Removing whitespace entirely, not collapsing it, is deliberate: parthpatil
    drops line breaks with no space ("Team,I am") while Tobi-Bueck keeps them
    ("Team,\\n\\nI am"). Collapsing would leave "team, i" vs "team,i" and hide
    genuine matches.
    """
    return (
        s.fillna("")
        .astype(str)
        .str.lower()
        .str.replace(r"\s+", "", regex=True)
    )


def header(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


# ---------------------------------------------------------------- parthpatil256
header(f"parthpatil256: {PARTH.name}")
parth = pd.read_csv(PARTH, index_col=0)  # file starts with an unnamed index column
print("Shape:", parth.shape)
print("Columns:", list(parth.columns))
print("\nDepartment value_counts():")
print(parth["Department"].value_counts(dropna=False))
print("\nPriority value_counts():")
print(parth["Priority"].value_counts(dropna=False))

# ---------------------------------------------------------------- alexandermeau
header(f"alexandermeau: {ALEX.name}")
alex = pd.read_csv(ALEX)
print("Shape:", alex.shape)
print("Columns:", list(alex.columns))

# Any routing-style column at the top level?
routing_words = ("team", "queue", "group", "department", "assign", "resolver")
routing_cols = [c for c in alex.columns if any(w in c.lower() for w in routing_words)]
print("\nTop-level routing-like columns:", routing_cols or "none")

# The ticket itself is stored as JSON; check its keys too.
ticket_keys = list(json.loads(alex["ticket"].iloc[0]).keys())
print("Keys inside ticket JSON (row 0):", ticket_keys)
routing_keys = [k for k in ticket_keys if any(w in k.lower() for w in routing_words)]
print("Routing-like keys inside ticket JSON:", routing_keys or "none")

# The closest thing to a label is the issue family. Print its counts if present.
family_cols = [c for c in alex.columns if "family" in c.lower() or "category" in c.lower()]
if family_cols:
    for col in family_cols:
        print(f"\n{col} value_counts():")
        print(alex[col].value_counts(dropna=False))
else:
    print("\nNo family/category column at the top level.")

# ---------------------------------------------------------------- overlap check
header("Overlap: parthpatil256 bodies found in Tobi-Bueck v5 (normalised)")
tobi = pd.read_csv(TOBI_V5)
parth_norm = normalise(parth["Body"])
tobi_norm = set(normalise(tobi["body"]))
tobi_norm.discard("")

non_empty = parth_norm != ""
found = parth_norm[non_empty].isin(tobi_norm)
print(f"parthpatil256 rows:              {len(parth_norm)}")
print(f"  with a non-empty body:         {int(non_empty.sum())}")
print(f"  body also in Tobi-Bueck v5:    {int(found.sum())} "
      f"({found.mean():.2%} of non-empty)")
print(f"Tobi-Bueck v5 unique bodies:     {len(tobi_norm)}")

# ---------------------------------------------------------------- v4 + v5 + language
header("Overlap: parthpatil256 bodies found in Tobi-Bueck v4 + v5, with language")
tobi_v4 = pd.read_csv(TOBI_V4)
both = pd.concat(
    [tobi_v4[["body", "language"]], tobi[["body", "language"]]],
    ignore_index=True,
)
both["norm"] = normalise(both["body"])
both = both[both["norm"] != ""]

# One row per (body, language) pair. If the same body appears with two
# different languages, the lookup would be ambiguous, so count those first.
pairs = both[["norm", "language"]].drop_duplicates()
is_conflict = pairs["norm"].duplicated(keep=False)
conflict_bodies = set(pairs.loc[is_conflict, "norm"])
print(f"(body, language) pairs in conflict: {int(is_conflict.sum())} "
      f"= {len(conflict_bodies)} bodies appearing with more than one language")

# Unambiguous bodies map to their language; conflicting ones are labelled
# "ambiguous" rather than silently resolved by row order.
lang_by_body = dict(zip(pairs.loc[~is_conflict, "norm"], pairs.loc[~is_conflict, "language"]))
lang_by_body.update({b: "ambiguous" for b in conflict_bodies})
parth_lang = parth_norm[non_empty].map(lang_by_body)  # NaN = no match found

matched = parth_lang.notna()
print(f"Non-empty parthpatil bodies:     {int(non_empty.sum())}")
print(f"  found in v4 + v5:              {int(matched.sum())} ({matched.mean():.2%})")
print("\nLanguage of parthpatil rows (via matched Tobi-Bueck body; NaN = unmatched):")
print(parth_lang.value_counts(dropna=False))

# ---------------------------------------------------------------- Tobi-Bueck subject
header("Tobi-Bueck v5, English rows: empty subject (after stripping whitespace)")
en = tobi[tobi["language"] == "en"]
subject_empty = en["subject"].fillna("").astype(str).str.strip() == ""
body_empty = en["body"].fillna("").astype(str).str.strip() == ""
print(f"English rows:                    {len(en)}")
print(f"  empty subject:                 {int(subject_empty.sum())} ({subject_empty.mean():.2%})")
print(f"  empty body:                    {int(body_empty.sum())}")
