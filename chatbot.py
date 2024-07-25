import traceback
from collections import defaultdict
import gc
from typing import Dict, List, Optional, TypedDict
import torch
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer, AutoModelForCausalLM
from config import Config


class Message(TypedDict):
    role: str
    content: str


class JazzyChatbot:
    def __init__(self) -> None:
        # load model
        self.tokenizer = AutoTokenizer.from_pretrained(Config.model_id)
        self.model = AutoAWQForCausalLM.from_pretrained(
            Config.model_id,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            device_map="cuda",
        )
        # stores all the convos for one chatbot as { id: msgs[] }
        self.convos: Dict[str, List[Message]] = defaultdict(list)

    def create_new_convo(self, convo_id: str, context: str = None):
        """Creates a new convo if nonexistent"""
        if self.convos.get(convo_id, None) is None:
            if context is not None:
                self.convos[convo_id] = [{"role": "system", "content": context}]
            else:
                self.convos[convo_id] = [
                    {"role": "system", "content": Config.default_context}
                ]

    def add_message_to_convo(
        self, convo_id: str, message: str, author: str
    ) -> Optional[str]:
        # create new convo if it didn't exist
        # terrible practice tbh, not pure func, but idc
        self.create_new_convo(convo_id)
        self.convos[convo_id].append({"role": author, "content": message})

    def respond_to_convo(self, convo_id: str):
        try:
            convo = self.convos[convo_id]
            inputs = self.tokenizer.apply_chat_template(
                convo,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt",
                return_dict=True,
            ).to(Config.device)

            input_len = inputs["input_ids"].shape[1]

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=Config.max_new_tokens,
                # default temp is 1?
                do_sample=True,
            )

            last_output = self.tokenizer.batch_decode(
                outputs[:, input_len:], skip_special_tokens=True
            )[0]
            self.add_message_to_convo(convo_id, last_output, "assistant")

            # cleaning? idk idr
            torch.cuda.empty_cache()
            gc.collect()

            return last_output
        except Exception as e:
            raise e

    def clear_convo(self, convo_id: str):
        if convo_id in self.convos:
            del self.convos[convo_id]

    def get_convo_context(self, convo_id: str):
        # create new convo if it didn't exist
        # terrible practice tbh, but idc
        self.create_new_convo(convo_id)
        return self.convos[convo_id][0]["content"]
