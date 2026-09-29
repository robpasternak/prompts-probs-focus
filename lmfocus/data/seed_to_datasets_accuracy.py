
import random
from pathlib import Path

import pandas as pd

from lmfocus.data.bracketing_models import ALL_BRACKETING_MODELS, BracketingModel
from lmfocus.data.utils import (
    replace_focus_with_all_caps,
    replace_focus_with_bracketing,
)


def create_all_caps_dataset(
    seed_csv_path: Path | str,
    output_csv_path: Path | str
):
    """
    Create a new dataset where the focused parts of the sentences are converted to all caps.
    """
    df_allcaps = pd.read_csv(seed_csv_path)
    df_allcaps['sentence_good'] = df_allcaps['sentence_good'].apply(replace_focus_with_all_caps)
    df_allcaps['sentence_bad'] = df_allcaps['sentence_bad'].apply(replace_focus_with_all_caps)
    df_allcaps['focus_prefix'] = ''
    df_allcaps['focus_suffix'] = ''
    df_allcaps.to_csv(output_csv_path, index=False)

def create_random_bracketings(
    num_bracketings: int = 20
):
    """
    Create a new dataset where the focused parts of the sentences are replaced with random bracketing styles.
    """
    characters = '@#$%;:'
    bracketings = []
    for i in range(num_bracketings):
        num_brackets = random.randint(3, 5)
        random_brackets = random.choices(characters, k=num_brackets)
        start_bracket = ''.join(random_brackets)
        end_bracket = ''.join(reversed(random_brackets))
        model = BracketingModel(
            name=f'random_bracket_{i}',
            start_bracket=start_bracket,
            end_bracket=end_bracket
        )
        if model not in bracketings:
            bracketings.append(model)
    return bracketings

def create_bracketing_datasets(
    seed_csv_path: Path | str,
    output_dir: Path | str,
    random_bracketings: int = 20
):
    """
    Create new datasets where the focused parts of the sentences are replaced with different bracketing styles.
    """
    df = pd.read_csv(seed_csv_path)
    random_bracketings = create_random_bracketings(num_bracketings=random_bracketings)
    for model in ALL_BRACKETING_MODELS + random_bracketings:
        df_bracketed = df.copy()
        df_bracketed['sentence_good'] = df_bracketed['sentence_good'].apply(
            lambda x: replace_focus_with_bracketing(x, model.start_bracket, model.end_bracket)  # noqa: B023
        )
        df_bracketed['sentence_bad'] = df_bracketed['sentence_bad'].apply(
            lambda x: replace_focus_with_bracketing(x, model.start_bracket, model.end_bracket)  # noqa: B023
        )
        df_bracketed['focus_prefix'] = model.start_bracket
        df_bracketed['focus_suffix'] = model.end_bracket
        output_csv_path = Path(output_dir) / f"{model.name}.csv"
        df_bracketed.to_csv(output_csv_path, index=False)

if __name__ == '__main__':
    seed_csv_path_one = Path(__file__).parent.parent.parent / 'data' / 'datasets_seed' / 'seed_data_1.csv'
    all_caps_output_csv_path_one = Path(__file__).parent.parent.parent / 'data' / 'datasets_1' / 'all_caps.csv'
    dataset_dir_one = Path(__file__).parent.parent.parent / 'data' / 'datasets_1'
    seed_csv_path_two = Path(__file__).parent.parent.parent / 'data' / 'datasets_seed' / 'seed_data_2.csv'
    all_caps_output_csv_path_two = Path(__file__).parent.parent.parent / 'data' / 'datasets_2' / 'all_caps.csv'
    dataset_dir_two = Path(__file__).parent.parent.parent / 'data' / 'datasets_2'
    create_all_caps_dataset(seed_csv_path=seed_csv_path_one, output_csv_path=all_caps_output_csv_path_one)
    create_bracketing_datasets(seed_csv_path=seed_csv_path_one, output_dir=dataset_dir_one, random_bracketings = 0)
    create_all_caps_dataset(seed_csv_path=seed_csv_path_two, output_csv_path=all_caps_output_csv_path_two)
    create_bracketing_datasets(seed_csv_path=seed_csv_path_two, output_dir=dataset_dir_two, random_bracketings = 0)