"""Used to export seed data from multi-sheet Excel file (not contained in this repo) to CSV."""

from pathlib import Path

import pandas as pd

SEED_EXCEL_SHEETS = {
    "only_data": "ONLY",
    "question_data": "QUESTION_ANSWER",
    "too_data": "TOO",
    "adv_quant_data": "ADV_QUANT",
    "contrast1_data": "CONTRAST1",
    "contrast2_data": "CONTRAST2",
}


def strings_equivalent_minus_focus(string1, string2):
    """
    Check if two strings are equivalent after removing focus markers (<<>>)
    """
    return string1.replace("<<", "").replace(">>", "") == string2.replace(
        "<<", ""
    ).replace(">>", "")


def excel_seed_to_csv(
    excel_path: Path | str, csv_path: Path | str, sheet_to_cat_mapping: dict[str, str]
):
    """
    Gather all of the data from the seed excel file and write it to a single CSV file.
    For each sheet, the data contains:
    - context (Optional): A string representing the preceding context. Should be pd.NA if
        this column is absent from the sheet.
    - prefix (Optional): A string representing the prefix. Should be pd.NA if this column
        is absent from the sheet.
    - sentence_good: A string representing the "good" sentence.
    - sentence_bad: A string representing the "bad" sentence.

    The output CSV should contain these four columns, plus the category column, whose value
    is determined by the sheet_to_cat_mapping argument.
    """
    df = pd.DataFrame(
        columns=["context", "prefix", "sentence_good", "sentence_bad", "category"]
    )
    for sheet_name in sheet_to_cat_mapping:  # noqa: PLC0206
        sheet_df = pd.read_excel(excel_path, sheet_name=sheet_name)
        sheet_df["category"] = sheet_to_cat_mapping[sheet_name]
        if "context" not in sheet_df.columns:
            sheet_df["context"] = pd.NA
        if "prefix" not in sheet_df.columns:
            sheet_df["prefix"] = pd.NA
        df = pd.concat(
            [
                df,
                sheet_df[
                    ["context", "prefix", "sentence_good", "sentence_bad", "category"]
                ],
            ],
            ignore_index=True,
        )
    df.to_csv(csv_path, index=False)


def check_seed_for_good_bad_match(
    seed_csv_path: Path | str,
):
    """
    Check that the good and bad sentences in the seed CSV match, ignoring focus markers (<<>>).
    """
    df = pd.read_csv(seed_csv_path)
    for index, row in df.iterrows():
        if not strings_equivalent_minus_focus(
            row["sentence_good"], row["sentence_bad"]
        ):
            raise ValueError(
                f"Good and bad sentences do not match at index {index}: "
                f"{row['sentence_good']} vs {row['sentence_bad']}"
            )


if __name__ == "__main__":
    excel_path_one = (
        Path(__file__).parent.parent.parent
        / "data"
        / "datasets_seed"
        / "seed_data_1.xlsx"
    )
    csv_path_one = (
        Path(__file__).parent.parent.parent
        / "data"
        / "datasets_seed"
        / "seed_data_1.csv"
    )
    excel_path_two = (
        Path(__file__).parent.parent.parent
        / "data"
        / "datasets_seed"
        / "seed_data_2.xlsx"
    )
    csv_path_two = (
        Path(__file__).parent.parent.parent
        / "data"
        / "datasets_seed"
        / "seed_data_2.csv"
    )
    excel_seed_to_csv(
        excel_path=excel_path_one,
        csv_path=csv_path_one,
        sheet_to_cat_mapping=SEED_EXCEL_SHEETS,
    )
    check_seed_for_good_bad_match(seed_csv_path=csv_path_one)
    excel_seed_to_csv(
        excel_path=excel_path_two,
        csv_path=csv_path_two,
        sheet_to_cat_mapping=SEED_EXCEL_SHEETS,
    )
    check_seed_for_good_bad_match(seed_csv_path=csv_path_two)
