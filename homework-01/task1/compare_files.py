import pandas as pd

for f in ["aa_dataset-tickets-multi-lang-5-2-50-version.csv",
          "dataset-tickets-multi-lang-4-20k.csv"]:
    df = pd.read_csv(f"data/raw/tobi-bueck/{f}")
    print("=" * 60)
    print(f, df.shape)
    print(df.columns.tolist())
    print(df["language"].value_counts(), "\n")
    print(df["queue"].value_counts())