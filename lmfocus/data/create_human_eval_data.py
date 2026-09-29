from pathlib import Path

import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv(
        Path(__file__).parent.parent.parent / "data" / "datasets_2" / "all_caps.csv"
    )
    # Select 8 random rows from each unique category (category column is 'category')
    # Make sure the category column remains
    df_sampled = (
        df.groupby("category").apply(lambda x: x.sample(8)).reset_index()
    )
    # Shuffle rows
    df_sampled = df_sampled.sample(frac=1).reset_index(drop=True)
    print(df_sampled.head())
    print(df_sampled.shape)
    df_sampled.to_csv(
        Path(__file__).parent.parent.parent
        / "data"
        / "datasets_2_human"
        / "human_test_data.csv",
        index=False,
    )
