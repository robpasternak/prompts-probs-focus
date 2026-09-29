uv run scripts/run_exp_accuracy.py --model "$@" --test-type string_probs --dataset 2 &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type string_probs --dataset 2 --control #&&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type forced_choice --dataset 2 --prompt 1 &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type forced_choice --dataset 2 --prompt 2 &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type forced_choice --dataset 2 --prompt 1 --control &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type forced_choice --dataset 2 --prompt 2 --control &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type yes_no --dataset 2 --prompt 1 &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type yes_no --dataset 2 --prompt 2 &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type yes_no --dataset 2 --prompt 1 --control &&
uv run scripts/run_exp_accuracy.py --model "$@" --test-type yes_no --dataset 2 --prompt 2 --control