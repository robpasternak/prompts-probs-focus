from itertools import product
from pathlib import Path

from lmfocus.utils import (
    ALL_MODELS,
    RANDOM_FOCUS_MARKERS,
    STANDARD_FOCUS_MARKERS,
    TestType,
)

ALL_FOCUS_MARKERS = STANDARD_FOCUS_MARKERS + RANDOM_FOCUS_MARKERS

if __name__ == '__main__':
    num_missing = 0
    for test_type, focus_marker, model in product(TestType, ALL_FOCUS_MARKERS, ALL_MODELS):
        top_folder_path = Path(__file__).parent.parent / 'data' / 'results' / test_type.value / 'dataset_2' / model
        middle_folder_paths = [top_folder_path] if test_type == TestType.STRING_PROBS else [(top_folder_path / 'prompt_1'), (top_folder_path / 'prompt_2')]
        bottom_folder_paths = [middle_folder_path / focus_marker for middle_folder_path in middle_folder_paths for focus_marker in ALL_FOCUS_MARKERS]
        for bottom_folder_path in bottom_folder_paths:
            if not (bottom_folder_path / 'results_1.csv').exists():
                print(f"Missing: {bottom_folder_path / 'results_1.csv'}")
                num_missing += 1
            if not (bottom_folder_path / 'control_results_1.csv').exists():
                print(f"Missing: {bottom_folder_path / 'control_results_1.csv'}")
                num_missing += 1
    print(f"Check complete. Total missing files: {num_missing}.")