from typing import Literal, Optional
from fastchat.conversation import Conversation, SeparatorStyle
import os


class Config:
    # model_path = f"{os.getenv('HOME')}/scratch/models/vicuna-7b"
    model_path = f"{os.getenv('HOME')}/scratch/models/vicuna-13b"
    device: Literal["cpu", "cuda", "mps"] = "cuda"
    num_gpus = 1
    # The maximum memory per gpu. Use a string like '13Gib'
    max_gpu_memory: Optional[str] = None
    load_8bit = False
    debug = False

    temperature = 0.7
    max_new_tokens = 512
    context_len = 2048

    convo_template = Conversation(
        system="A chat between a hooman and a jazzy but intelligent cat. "
        "The cat understands its memes, and is pretty jazzy. Being a cat, it sometimes goes ':BLEHH:'. "
        "But, the cat does give helpful and detailed answers to the hooman questions and requests (most of the time). "
        "After all, despite being a jazzy and memey cat, it's pretty wise and is a pretty nice cat. ",
        roles=("HOOMAN", "JAZZYCAT"),
        messages=(),
        offset=0,
        sep_style=SeparatorStyle.TWO,
        sep=" ",
        sep2="</s>",
    )
    # convo_template = Conversation(
    #     system="A chat between a curious user and an artificial intelligence assistant. "
    #     "The assistant gives helpful, detailed, and polite answers to the user's questions.",
    #     roles=("USER", "ASSISTANT"),
    #     messages=(),
    #     offset=0,
    #     sep_style=SeparatorStyle.TWO,
    #     sep=" ",
    #     sep2="</s>",
    # )

    # positive integer, or -1 for no limit
    responses_to_generate_limit = 2
