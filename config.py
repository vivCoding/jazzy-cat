from typing import Literal, Optional
from fastchat.conversation import Conversation, SeparatorStyle
import os


class Config:
    model_path = f"{os.getenv('HOME')}/scratch/models/vicuna-7b"
    # model_path = f"{os.getenv('HOME')}/scratch/models/vicuna-13b"
    device: Literal["cpu", "cuda", "mps"] = "cuda"
    num_gpus = 1
    # The maximum memory per gpu. Use a string like '13Gib'
    max_gpu_memory: Optional[str] = None
    load_8bit = False
    debug = False

    temperature = 0.7
    max_new_tokens = 100
    context_len = 2048

    convo = Conversation(
        system="A chat between some tired CS students and bums, and one jazzy but intelligent AI cat."
        "The cat tiredly gives helpful and detailed answers. It likes using memes. It's pretty jazzy.",
        roles=("PERSON", "JAZZY CAT"),
        messages=(),
        offset=0,
        sep_style=SeparatorStyle.TWO,
        sep=" ",
        sep2="</s>",
    )

    # positive integer, or -1 for no limit
    requests_to_generate_limit = 4
