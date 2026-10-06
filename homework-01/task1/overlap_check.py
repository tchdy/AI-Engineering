import pandas as pd

old = pd.read_csv("data/raw/tobi-bueck/dataset-tickets-multi-lang-4-20k.csv")
new = pd.read_csv("data/raw/tobi-bueck/aa_dataset-tickets-multi-lang-5-2-50-version.csv")

overlap = old["body"].isin(new["body"]).sum()
print(f"{overlap} of {len(old)} old bodies appear in the new file "
      f"({overlap / len(old):.1%})")