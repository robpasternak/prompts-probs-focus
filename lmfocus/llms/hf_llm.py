import re
from enum import Enum

from minicons import scorer
from tqdm import tqdm
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Llama4ForCausalLM,
    Mistral3ForConditionalGeneration,
)


class LLMType(str, Enum):
    HF_GENERAL = "hf_general"
    LLAMA_4 = "llama_4"
    MISTRAL = "mistral"


LLM_TYPE_TO_MODEL_CLASS = {
    LLMType.HF_GENERAL: AutoModelForCausalLM,
    LLMType.LLAMA_4: Llama4ForCausalLM,
    LLMType.MISTRAL: Mistral3ForConditionalGeneration,
}


class HFLLM:
    def __init__(
        self,
        model_name,
        model_type: LLMType = LLMType.HF_GENERAL,
        instruct=False,
        quantize=False,
        is_thinking_model=False,
        device="auto",
    ):
        self.device = device
        model_class = LLM_TYPE_TO_MODEL_CLASS[model_type]
        self.is_thinking_model = is_thinking_model
        if quantize:
            # Load model from Hugging Face and use bits and bytes to quantize
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
            )
            self.model = model_class.from_pretrained(
                model_name,
                quantization_config=quantization_config,
                device_map=self.device,
                offload_folder="./offload",
            )
        else:
            self.model = model_class.from_pretrained(
                model_name, device_map=self.device, offload_folder="./offload"
            )

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.ilm = scorer.IncrementalLMScorer(
            model=self.model, device=self.device, tokenizer=self.tokenizer
        )
        self.instruct = instruct
        self.quantize = quantize

    def make_prob_prompt_instruct(self, messages: list[dict]):
        if self.instruct:
            final_message = messages[-1] if messages else None
            kwargs = {
                "continue_final_message": bool(
                    messages and messages[-1]["role"] == "assistant"
                ),
                "add_generation_prompt": not (
                    messages and messages[-1]["role"] == "assistant"
                ),
            }
            if self.is_thinking_model:
                kwargs["enable_thinking"] = False
            rendered_prompt = self.tokenizer.apply_chat_template(
                messages, tokenize=False, **kwargs
            )
            if final_message and final_message["role"] == "assistant":
                trailing_whitespace = re.search(r"\s+$", final_message["content"])
                if trailing_whitespace:
                    suffix = trailing_whitespace.group(0)
                    if not rendered_prompt.endswith(suffix):
                        rendered_prompt += suffix
            return rendered_prompt
        else:
            return ValueError(
                "make_prob_prompt_instruct is only applicable when instruct=True"
            )

    def get_sum_logprobs(self, prefixes, sentences, description=None):
        data = []
        for prompt, sentence in tqdm(
            zip(prefixes, sentences), total=len(prefixes), desc=description
        ):
            data.extend(
                self.ilm.conditional_score(
                    prefix=[prompt],
                    stimuli=[sentence],
                    reduction=lambda x: x.sum(0).item(),
                )
            )
        return data


if __name__ == "__main__":
    model = HFLLM(model_name="Qwen/Qwen2.5-7B-Instruct", instruct=True, device="mps")

    contexts = [
        """There was a big party on the university campus. Most of the attendees were donors, but there were also three students and three deans. The deans were named Ann, Bill, and Charlie. At the party, 
- Ann met two of the three students.
- Bill met all three students.
- Charlie did not meet any of the three students."""
    ] * 3

    sentences = [
        "No student met Ann.",
        "No student met Bill.",
        "No student met Charlie.",
    ]

    results = model.get_sum_logprobs(
        prefixes=[[{"role": "user", "content": context}] for context in contexts],
        sentences=sentences,
    )
    print(results)
