from enum import Enum

STANDARD_FOCUS_MARKERS = [
    "all_caps",
    "html_bold",
    "html_emphasis",
    "html_italics",
    "html_underline",
    "markdown_bold",
    "markdown_emphasis",
    "markdown_italics",
]

RANDOM_FOCUS_MARKERS = [f"random_bracket_{i}" for i in range(10)]

class TestType(str, Enum):
    STRING_PROBS = "string_probs"
    FORCED_CHOICE = "forced_choice"
    YES_NO = "yes_no"

MODEL_NAME_MAPPING = {
    'gemma_4_E2B': 'Gemma 4 E2B',
    'gemma_4_E4B': 'Gemma 4 E4B',
    'gemma_4_12B': 'Gemma 4 12B',
    'gemma_4_26B_A4B': 'Gemma 4 26B A4B',
    'gemma_4_31B': 'Gemma 4 31B',
    'qwen_3_0.6B': 'Qwen3 0.6B',
    'qwen_3_1.7B': 'Qwen3 1.7B',
    'qwen_3_4B': 'Qwen3 4B',
    'qwen_3_8B': 'Qwen3 8B',
    'qwen_3_14B': 'Qwen3 14B',
    'qwen_3_32B': 'Qwen3 32B',
    "qwen_3.5_0.8B": "Qwen3.5 0.8B",
    "qwen_3.5_2B": "Qwen3.5 2B",
    "qwen_3.5_4B": "Qwen3.5 4B",
    "qwen_3.5_9B": "Qwen3.5 9B",
    "qwen_3.5_27B": "Qwen3.5 27B",
    "qwen_3.5_35B_A3B": "Qwen3.5 35B A3B"
}

GEMMA_MODELS = [
    'gemma_4_E2B',
    'gemma_4_E4B',
    'gemma_4_12B',
    'gemma_4_26B_A4B',
    'gemma_4_31B',
]

QWEN_3_MODELS = [
    'qwen_3_0.6B',
    'qwen_3_1.7B',
    'qwen_3_4B',
    'qwen_3_8B',
    'qwen_3_14B',
    'qwen_3_32B',
]

QWEN_35_MODELS = [
    "qwen_3.5_0.8B",
    "qwen_3.5_2B",
    "qwen_3.5_4B",
    "qwen_3.5_9B",
    "qwen_3.5_27B",
    "qwen_3.5_35B_A3B",
]

ALL_MODELS = GEMMA_MODELS + QWEN_3_MODELS + QWEN_35_MODELS

MODEL_SIZES = {
    'gemma_4_E2B': 2,
    'gemma_4_E4B': 4,
    'gemma_4_12B': 12,
    'gemma_4_26B_A4B': 26,
    'gemma_4_31B': 31,
    'qwen_3_0.6B': 0.6,
    'qwen_3_1.7B': 1.7,
    'qwen_3_4B': 4,
    'qwen_3_8B': 8,
    'qwen_3_14B': 14,
    'qwen_3_32B': 32,
    "qwen_3.5_0.8B": 0.8,
    "qwen_3.5_2B": 2,
    "qwen_3.5_4B": 4,
    "qwen_3.5_9B": 9,
    "qwen_3.5_27B": 27,
    "qwen_3.5_35B_A3B": 35,
}

DATA_TYPE_TRANSLATION = {
    'string_probs' : 'SP',
    'forced_choice_1': 'FC1',
    'forced_choice_2': 'FC2',
    'yes_no_1': 'YN1',
    'yes_no_2': 'YN2'
}

CATEGORY_TRANSLATION = {
    "ONLY": "ONLY",
    "ADV_QUANT": "ADV_QT",
    "TOO": "TOO",
    "QUESTION_ANSWER": "QA",
    "CONTRAST1": "CONTR1",
    "CONTRAST2": "CONTR2"
}

FM_TRANSLATION = {
    "all_caps": "All Caps",
    "html_bold": "HTML Bold",
    "html_emphasis": "HTML Emphasis",
    "html_italics": "HTML Italics",
    "html_underline": "HTML Underline",
    "markdown_bold": "Markdown Bold",
    "markdown_emphasis": "Markdown Emphasis",
    "markdown_italics": "Markdown Italics",
    "random_bracket_0": "Random Bracket 0",
    "random_bracket_1": "Random Bracket 1",
    "random_bracket_2": "Random Bracket 2",
    "random_bracket_3": "Random Bracket 3",
    "random_bracket_4": "Random Bracket 4",
    "random_bracket_5": "Random Bracket 5",
    "random_bracket_6": "Random Bracket 6",
    "random_bracket_7": "Random Bracket 7",
    "random_bracket_8": "Random Bracket 8",
    "random_bracket_9": "Random Bracket 9"
}

METHODS_PALETTE = {
    "SP": "#1077E5",
    "FC1": "#62182F",
    "FC2": "#C5305F",
    "YN1": "#F55200",
    "YN2": "#FF925C"
}