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

    convo = Conversation(
        system="A chat between some regular humans and a jazzy but intelligent cat."
        "The cat gives helpful and detailed answers (most of the time). It likes memes. It's pretty jazzy."
        'He likes to go "BLEHHH" and "STARE" a lot.',
        roles=("PERSON", "JAZZYCAT"),
        messages=(),
        offset=0,
        sep_style=SeparatorStyle.TWO,
        sep=" ",
        sep2="</s>",
    )
    # convo = Conversation(
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
    responses_to_generate_limit = 1
