"""Utility functions for parsing results and descriptive statistics."""

from itertools import product
from pathlib import Path

import pandas as pd

from lmfocus.utils import STANDARD_FOCUS_MARKERS, TestType  #TOKENIZERS

ALL_TEST_TYPES = [TestType.STRING_PROBS, TestType.FORCED_CHOICE, TestType.YES_NO]


def accuracy_calc(df: pd.DataFrame, focus_marker, focus_prefix, data_type="string_probs"):
    out_df = df.groupby("original_data_index", as_index=False).agg(
        logprob_difference=("logprob_difference", "sum"),
        output_good=("output_good", "first"),
        output_bad=("output_bad", "first"),
        output_good_logprob=("output_good_logprob", "sum"),
        output_bad_logprob=("output_bad_logprob", "sum"),
        category=("category", "first")
    )
    out_df["correct"] = out_df["logprob_difference"].gt(0)
    out_df["focus_marker"] = focus_marker
    out_df["focus_prefix"] = focus_prefix
    out_df["data_type"] = data_type
    return out_df[
        [
            "original_data_index",
            "correct",
            "focus_marker",
            "focus_prefix",
            "data_type",
            "category",
            "output_good",
            "output_bad",
            "output_good_logprob",
            "output_bad_logprob",
            'logprob_difference'
        ]
    ]


def accuracy_calc_even_only(df, focus_marker, data_type="string_probs"):
    if data_type == "string_probs" or data_type.startswith("forced_choice"):
        out_df = (
            df.groupby(
                ["noun_subject", "noun_object", "verb", "adv_position"], as_index=False
            )
            .agg(logprob_difference=("logprob_difference", "sum"))
            .pivot(
                index=["noun_subject", "noun_object", "verb"],
                columns="adv_position",
                values="logprob_difference",
            )
            .reset_index()
        )

        out_df["correct"] = out_df["vp"] > out_df["initial"]
    else:
        # Do the same as above, except: a given item is considered correct if the difference between the logprob_difference for 'even' vs. 'only' is greater when adv_position is 'vp' than when it is 'initial':
        print(data_type)
        out_df = (
            df.groupby(
                ["noun_subject", "noun_object", "verb", "adv_position", "adverb"],
                as_index=False,
            )
            .agg(logprob_difference=("logprob_difference", "sum"))
            .pivot(
                index=["noun_subject", "noun_object", "verb"],
                columns=["adv_position", "adverb"],
                values="logprob_difference",
            )
            .reset_index()
        )

        out_df["correct"] = (out_df[("vp", "even")] - out_df[("vp", "only")]) > (
            out_df[("initial", "even")] - out_df[("initial", "only")]
        )

        out_df.columns = [col[0] for col in out_df.columns if isinstance(col, tuple)]

    out_df.columns.names = [None]

    out_df["focus_marker"] = focus_marker
    out_df["data_type"] = data_type

    return out_df[
        ["noun_subject", "noun_object", "verb", "correct", "focus_marker", "data_type"]
    ]

# def add_token_counts(df):
#     out_df = df.copy()
#     out_df['output_good_token_count'] = df.apply(lambda row: len(TOKENIZERS[row['model']].tokenize(row['output_good'])), axis=1)
#     out_df['output_bad_token_count'] = df.apply(lambda row: len(TOKENIZERS[row['model']].tokenize(row['output_bad'])), axis=1)
#     return out_df


def gather_data_accuracy(
    models: list[str],
    results_folder: str,
    dataset: int,
    test_types: list[TestType] = ALL_TEST_TYPES,
    focus_markers: list[str] = STANDARD_FOCUS_MARKERS,
    control=False,
):
    control_str = "control_" if control else ""
    dfs = []
    for model, test_type in product(models, test_types):
        prompt_strings = (
            ["/prompt_1", "/prompt_2"] if test_type != TestType.STRING_PROBS else [""]
        )
        for prompt_string in prompt_strings:
            for focus_marker in focus_markers:
                results_folder_path = (
                    Path(results_folder)
                    / test_type.value
                    / f"dataset_{dataset}"
                    / f"{model}{prompt_string}"
                    / focus_marker
                    / f"{control_str}results_1.csv"
                )
                if results_folder_path.exists():
                    data_type = (
                        test_type.value
                        if test_type == TestType.STRING_PROBS
                        else f"{test_type.value}_{prompt_string[-1]}"
                    )
                    df = pd.read_csv(results_folder_path)
                    new_df = accuracy_calc(
                        df=df,
                        focus_marker=focus_marker,
                        focus_prefix=df['focus_prefix'][0],
                        data_type=data_type,
                    )
                    new_df["model"] = model
                    # new_df = add_token_counts(new_df)
                    dfs.extend([new_df])
    if not dfs:
        return pd.DataFrame()
    out_df = pd.concat(dfs)
    out_df["condition"] = "Control" if control else "Target"
    return out_df
