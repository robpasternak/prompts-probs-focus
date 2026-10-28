import argparse
import json
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from lmfocus.data.data_transformations import DATA_CONVERTERS
from lmfocus.llms import HFLLM
from lmfocus.utils import RANDOM_FOCUS_MARKERS, STANDARD_FOCUS_MARKERS, TestType

load_dotenv()

ALL_DATASETS = STANDARD_FOCUS_MARKERS + RANDOM_FOCUS_MARKERS


with (Path(__file__).parent / "models.json").open() as f:
    MODEL_INFO = json.load(f)


def parse_args() -> argparse.Namespace:
    """
    Parse CLI arguments.

    --model <str>: Model key from scripts.models.json
    --focus-types <str>: Focus types (comma-separated, no space), defaults to all (excluding randomly-generated)
    --batch-size <int>: Batch size for saving output CSVs (default: all rows, i.e. single batch)
    --quantize: Flag to 8-bit quantize the model (default: False)
    --dataset: Which dataset to use (1 or 2)
    --test-type <str>: Type of test to run (choices: string_probs, forced_choice, yes_no; default: string_probs)
    --prompt <int>: Index of the judgment prompt to use (default: 1)
    --device <str>: Device to run the model on (default: auto)
    --save-folder-suffix <str>: Suffix to append to the save folder name (default: "")
    --control <bool>: Whether the test is a control test (default: False). Only affects string probability tests.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", required=True, help="Model key from scripts/models.json"
    )
    parser.add_argument(
        "--focus-types",
        required=False,
        default=",".join(STANDARD_FOCUS_MARKERS),
        help="Dataset names (without .csv extension, comma-separated), defaults to all datasets (excluding randomly-generated)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size for saving output CSVs (default: all rows, i.e. single batch)",
    )
    parser.add_argument(
        "--quantize",
        action=argparse.BooleanOptionalAction,
        help="Flag to 8-bit quantize the model (default: False)",
    )
    parser.add_argument(
        "--dataset",
        type=int,
        help="Which dataset to use (defaults to 1)",
    )
    parser.add_argument(
        "--test-type",
        type=str,
        choices=[e.value for e in TestType],
        default=TestType.STRING_PROBS.value,
        help="Type of test to run (default: string_probs)",
    )
    parser.add_argument(
        "--prompt",
        type=int,
        default=1,
        help="Index of the judgment prompt to use (default: 1). Only relevant for judge tasks.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="auto",
        help="Device to run the model on (default: auto)",
    )
    parser.add_argument(
        "--save-folder-suffix",
        type=str,
        default="",
        help="Suffix to append to the save folder name (default: '')",
    )
    parser.add_argument(
        "--control",
        action=argparse.BooleanOptionalAction,
        help="Whether the test is a control test (default: False). Only affects string probability tests.",
    )
    return parser.parse_args()


def calculate_accuracy_num_dom(
    batch_df: pd.DataFrame,
) -> list[float]:
    # Returns a pair of a numerator and a denominator, where the numerator is the number
    # of correct judgments and the denominator is the total number of judgments.
    grouped = batch_df.groupby("original_data_index")["logprob_difference"].sum()
    return sum(grouped.gt(0).astype(int)), len(grouped)


def run_experiment(
    model_json_name: str,
    focus_types: str,
    test_type: TestType = TestType.STRING_PROBS,
    batch_size: int | None = None,
    quantize: bool = False,
    prompt: int = 1,
    device: str = "auto",
    dataset: int = 1,
    save_folder_suffix: str = "",
    control: bool = False,
) -> None:
    """
    Run the experiment with the specified parameters.

    Args:
        model_json_name (str): Name of the model JSON configuration.
        focus_types (str): Comma-separated list of focus types.
        test_type (TestType): Type of test to run (default: STRING_PROBS).
        batch_size (int | None): Batch size for evaluation (default: None).
        quantize (bool): Whether to quantize the model (default: False).
        prompt (int): Index of the judgment prompt to use (default: 1). Only relevant for judge tasks.
        device (str): Device to run the model on (default: auto).
    """
    if focus_types == "ALL":
        focus_type_list = ALL_DATASETS
    elif focus_types == "RANDOM":
        focus_type_list = RANDOM_FOCUS_MARKERS
    else:
        focus_type_list = [name.strip() for name in focus_types.split(",")]
    if batch_size is not None and batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")

    # Initialize the model
    model_name = MODEL_INFO[model_json_name]["model_name"]
    model_kwargs = MODEL_INFO[model_json_name].get("model_kwargs", {})
    model_kwargs["quantize"] = model_kwargs.get("quantize", False) or quantize
    model_loaded = False

    control_prefix = "control_" if control else ""

    for focus_type in focus_type_list:
        # Prep folder for storing results

        save_folder_name = focus_type + save_folder_suffix
        output_dir = (
            Path(__file__).parent.parent
            / "data"
            / "results"
            / test_type.value
            / f"dataset_{dataset}"
            / model_json_name
        )
        if test_type in [TestType.FORCED_CHOICE, TestType.YES_NO]:
            output_dir = output_dir / f"prompt_{prompt}" / save_folder_name
        else:
            output_dir = output_dir / save_folder_name

        output_dir.mkdir(parents=True, exist_ok=True)

        if (output_dir / f"{control_prefix}results_1.csv").exists():
            prompt_string = (
                f" and prompt {prompt}"
                if test_type in [TestType.FORCED_CHOICE, TestType.YES_NO]
                else ""
            )
            control_string = " (control)" if control else ""
            print(
                f"Results already exist for model '{model_json_name}' with focus marker '{focus_type}' and test type '{test_type.value}', using dataset {dataset}{prompt_string}{control_string}."
            )
            continue


        if not model_loaded:
            model = HFLLM(model_name=model_name, device=device, **model_kwargs)
            model_loaded = True

        print(
            f"Running experiment for model '{model_json_name}' with focus marker '{focus_type}' and test type '{test_type.value}'"
        )
        print(f"Using dataset {dataset}.")
        if test_type in [TestType.FORCED_CHOICE, TestType.YES_NO]:
            print(f"Using prompt {prompt}.")
        if control:
            print("Running control test.")

        # Load dataset and divide into batches
        eval_csv_path = (
            Path(__file__).parent.parent
            / "data"
            / f"datasets_{dataset}"
            / f"{focus_type}.csv"
        )
        eval_df = pd.read_csv(eval_csv_path)
        transformed_data = DATA_CONVERTERS[test_type.value](
            df=eval_df, llm=model, prompt_name=f"prompt_{prompt}", control=control
        )
        total_rows = len(transformed_data)
        print(total_rows, "rows of transformed data ready for evaluation.")
        run_batch_size = batch_size or total_rows
        total_batches = max(1, (total_rows + run_batch_size - 1) // run_batch_size)
        batch_index_width = len(str(total_batches))

        for batch_idx, start in enumerate(
            range(0, total_rows, run_batch_size), start=1
        ):
            end = min(start + run_batch_size, total_rows)
            batch_df = transformed_data.iloc[start:end].copy()
            batch_results_good = model.get_sum_logprobs(
                prefixes=batch_df["model_prefix"].tolist(),
                sentences=batch_df["output_good"].tolist(),
                description=f"Batch {batch_idx}/{total_batches} - Good Outputs",
            )
            batch_df["output_good_logprob"] = batch_results_good
            batch_results_bad = model.get_sum_logprobs(
                prefixes=batch_df["model_prefix"].tolist(),
                sentences=batch_df["output_bad"].tolist(),
                description=f"Batch {batch_idx}/{total_batches} - Bad Outputs",
            )
            batch_df["output_bad_logprob"] = batch_results_bad
            batch_df["logprob_difference"] = (
                batch_df["output_good_logprob"] - batch_df["output_bad_logprob"]
            )

            batch_accuracy_numerator, batch_accuracy_denominator = (
                calculate_accuracy_num_dom(batch_df)
            )

            print(f"Batch {batch_idx}/{total_batches} results:")
            print(
                f"Mean good response logprob: {batch_df['output_good_logprob'].mean()}"
            )
            print(f"Mean bad response logprob: {batch_df['output_bad_logprob'].mean()}")
            print(f"Mean logprob difference: {batch_df['logprob_difference'].mean()}")
            print(
                f"Total correct: {batch_accuracy_numerator}/{batch_accuracy_denominator}"
            )
            print(
                f"Batch accuracy: {batch_accuracy_numerator / batch_accuracy_denominator * 100:.1f}%"
            )

            out_file = (
                output_dir
                / f"{control_prefix}results_{batch_idx:0{batch_index_width}d}.csv"
            )
            print(f"Saving batch {batch_idx}/{total_batches} to {out_file}")
            batch_df.to_csv(str(out_file), index=False)


if __name__ == "__main__":
    args = parse_args()
    run_experiment(
        model_json_name=args.model,
        focus_types=args.focus_types,
        test_type=TestType(args.test_type),
        batch_size=args.batch_size,
        quantize=args.quantize,
        prompt=args.prompt,
        device=args.device,
        dataset=args.dataset,
        save_folder_suffix=args.save_folder_suffix,
        control=args.control,
    )
