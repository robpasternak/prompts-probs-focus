"""Transforms datasets for running experiments with each methodology."""

import json
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

from lmfocus.data.utils import capitalize_first_letter
from lmfocus.llms.hf_llm import HFLLM


class ExperimentRowAccuracy(BaseModel):
    original_data_index: int
    model_prefix: str
    output_good: str
    output_bad: str
    category: str
    focus_prefix: str
    focus_suffix: str


with (
    Path(__file__).parent.parent / "prompts" / "forced_choice" / "lm_prefixes.json"
).open() as f:
    FC_PROMPT_LM_PREFIX = json.load(f)

with (
    Path(__file__).parent.parent / "prompts" / "yes_no" / "lm_prefixes.json"
).open() as f:
    YES_NO_PROMPT_LM_PREFIX = json.load(f)


def string_prob_conversion(
    df: pd.DataFrame, llm: HFLLM, control: bool = False, **kwargs
) -> list[ExperimentRowAccuracy]:
    data = []
    for index, row in df.iterrows():
        # Create model prefix
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        focus_prefix = str(
            row["focus_prefix"] if not pd.isna(row["focus_prefix"]) else ""
        )
        focus_suffix = str(
            row["focus_suffix"] if not pd.isna(row["focus_suffix"]) else ""
        )
        if not control:
            if row.get("context") not in ["", None] and not pd.isna(row.get("context")):
                messages.append({"role": "user", "content": row["context"]})
            else:
                messages.append({"role": "user", "content": ""})
            if row["category"] in ["ONLY", "ADV_QUANT"]:
                messages.append({"role": "assistant", "content": "Therefore, "})
            if row["category"] in ["TOO", "CONTRAST2"]:
                messages.append(
                    {
                        "role": "assistant",
                        "content": capitalize_first_letter(
                            row["prefix"], focus_prefix
                        ).strip()
                        + " ",
                    }
                )
        else:
            messages.append({"role": "user", "content": ""})
        model_prefix = llm.make_prob_prompt_instruct(messages)

        # Create outputs
        output_good = (
            capitalize_first_letter(row["sentence_good"], focus_prefix)
            if row["category"] in ["QUESTION_ANSWER", "CONTRAST1", "CONTRAST2"]
            else row["sentence_good"]
        )
        output_bad = (
            capitalize_first_letter(row["sentence_bad"], focus_prefix)
            if row["category"] in ["QUESTION_ANSWER", "CONTRAST1", "CONTRAST2"]
            else row["sentence_bad"]
        )

        # Append data
        data.append(
            ExperimentRowAccuracy(
                original_data_index=index,
                model_prefix=model_prefix,
                output_good=output_good,
                output_bad=output_bad,
                category=row["category"],
                focus_prefix=focus_prefix,
                focus_suffix=focus_suffix,
            )
        )

    return pd.DataFrame([row.model_dump() for row in data])


def forced_choice_conversion(
    df: pd.DataFrame, llm: HFLLM, prompt_name: str, control: bool = False, **kwargs
) -> list[ExperimentRowAccuracy]:
    data = []
    with (
        Path(__file__).parent.parent
        / "prompts"
        / "forced_choice"
        / f"{prompt_name}.txt"
    ).open() as f:
        prompt_template = f.read()
    for index, row in df.iterrows():
        focus_prefix = str(
            row["focus_prefix"] if not pd.isna(row["focus_prefix"]) else ""
        )
        focus_suffix = str(
            row["focus_suffix"] if not pd.isna(row["focus_suffix"]) else ""
        )
        if pd.notna(row["context"]):
            context = row["context"].strip() if not control else ""
            sentence_good = capitalize_first_letter(row["sentence_good"], focus_prefix)
            sentence_bad = capitalize_first_letter(row["sentence_bad"], focus_prefix)
        else:
            context = (
                (
                    capitalize_first_letter(row["prefix"], focus_prefix).strip()[:-1]
                    + "..."
                )
                if not control
                else ""
            )
            sentence_good = "..." + row["sentence_good"]
            sentence_bad = "..." + row["sentence_bad"]

        instruction_template = prompt_template.format(context=context)

        model_messages_good_a = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": instruction_template.replace(
                    "SENTENCE_A", sentence_good
                ).replace("SENTENCE_B", sentence_bad),
            },
        ]

        model_messages_good_b = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": instruction_template.replace(
                    "SENTENCE_A", sentence_bad
                ).replace("SENTENCE_B", sentence_good),
            },
        ]

        if FC_PROMPT_LM_PREFIX[prompt_name]:
            model_messages_good_a.append(
                {"role": "assistant", "content": FC_PROMPT_LM_PREFIX[prompt_name]}
            )
            model_messages_good_b.append(
                {"role": "assistant", "content": FC_PROMPT_LM_PREFIX[prompt_name]}
            )

        model_prefix_good_a = llm.make_prob_prompt_instruct(model_messages_good_a)
        model_prefix_good_b = llm.make_prob_prompt_instruct(model_messages_good_b)

        data.extend(
            [
                ExperimentRowAccuracy(
                    original_data_index=index,
                    model_prefix=model_prefix_good_a,
                    output_good="A",
                    output_bad="B",
                    category=row["category"],
                    focus_prefix=focus_prefix,
                    focus_suffix=focus_suffix,
                ),
                ExperimentRowAccuracy(
                    original_data_index=index,
                    model_prefix=model_prefix_good_b,
                    output_good="B",
                    output_bad="A",
                    category=row["category"],
                    focus_prefix=focus_prefix,
                    focus_suffix=focus_suffix,
                ),
            ]
        )

    return pd.DataFrame([row.model_dump() for row in data])


def yes_no_conversion(
    df: pd.DataFrame, llm: HFLLM, prompt_name: str, control: bool = False, **kwargs
) -> list[ExperimentRowAccuracy]:
    data = []
    with (
        Path(__file__).parent.parent / "prompts" / "yes_no" / f"{prompt_name}.txt"
    ).open() as f:
        prompt_template = f.read()
    for index, row in df.iterrows():
        focus_prefix = str(
            row["focus_prefix"] if not pd.isna(row["focus_prefix"]) else ""
        )
        focus_suffix = str(
            row["focus_suffix"] if not pd.isna(row["focus_suffix"]) else ""
        )
        if pd.notna(row["context"]):
            context = row["context"].strip() if not control else ""
            sentence_good = capitalize_first_letter(row["sentence_good"], focus_prefix)
            sentence_bad = capitalize_first_letter(row["sentence_bad"], focus_prefix)
        else:
            context = (
                (
                    capitalize_first_letter(row["prefix"], focus_prefix).strip()[:-1]
                    + "..."
                )
                if not control
                else ""
            )
            sentence_good = "..." + row["sentence_good"]
            sentence_bad = "..." + row["sentence_bad"]

        instruction_template = prompt_template.format(context=context)

        model_messages_good = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": instruction_template.replace("TEST_SENTENCE", sentence_good),
            },
        ]

        model_messages_bad = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": instruction_template.replace("TEST_SENTENCE", sentence_bad),
            },
        ]

        if YES_NO_PROMPT_LM_PREFIX[prompt_name]:
            model_messages_good.append(
                {"role": "assistant", "content": YES_NO_PROMPT_LM_PREFIX[prompt_name]}
            )
            model_messages_bad.append(
                {"role": "assistant", "content": YES_NO_PROMPT_LM_PREFIX[prompt_name]}
            )

        model_prefix_good = llm.make_prob_prompt_instruct(model_messages_good)
        model_prefix_bad = llm.make_prob_prompt_instruct(model_messages_bad)

        data.extend(
            [
                ExperimentRowAccuracy(
                    original_data_index=index,
                    model_prefix=model_prefix_good,
                    output_good="Yes",
                    output_bad="No",
                    category=row["category"],
                    focus_prefix=focus_prefix,
                    focus_suffix=focus_suffix,
                ),
                ExperimentRowAccuracy(
                    original_data_index=index,
                    model_prefix=model_prefix_bad,
                    output_good="No",
                    output_bad="Yes",
                    category=row["category"],
                    focus_prefix=focus_prefix,
                    focus_suffix=focus_suffix,
                ),
            ]
        )

    return pd.DataFrame([row.model_dump() for row in data])


DATA_CONVERTERS = {
    "string_probs": string_prob_conversion,
    "forced_choice": forced_choice_conversion,
    "yes_no": yes_no_conversion,
}
