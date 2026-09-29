uv run scripts/run_exp_accuracy.py --model "$@" --test-type string_probs --dataset 2 --focus-types RANDOM &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type string_probs --dataset 2 --focus-types RANDOM --control &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type forced_choice --dataset 2 --focus-types RANDOM --prompt 1 &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type forced_choice --dataset 2 --focus-types RANDOM --prompt 2 &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type forced_choice --dataset 2 --focus-types RANDOM --prompt 1 --control &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type forced_choice --dataset 2 --focus-types RANDOM --prompt 2 --control &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type yes_no --dataset 2 --focus-types RANDOM --prompt 1 &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type yes_no --dataset 2 --focus-types RANDOM --prompt 2 &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type yes_no --dataset 2 --focus-types RANDOM --prompt 1 --control &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type yes_no --dataset 2 --focus-types RANDOM --prompt 2 --control

# Models remaining:
# gemma_4_31B
# olmo_3_7B
# qwen_3_4B