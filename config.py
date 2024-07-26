from typing import Literal, Optional
import os


class Config:
    # model_id = f"{os.getenv('HOME')}/scratch/models/Meta-Llama-3.1-8B-Instruct-AWQ-INT4"
    # model_quantized = True
    model_id = f"{os.getenv('RCAC_SCRATCH')}/models/Meta-Llama-3.1-8B-Instruct"
    model_quantized = True
    device: Literal["cpu", "cuda"] = "cuda"

    max_new_tokens = 1000

    default_context = """You are a helpful tech bro, named "jazzy cat", talking to a bunch of tech bros on a Discord server."""
    serious_context = "You are a helpful assistant, who gives detailed answers in a professional manner."

    log_file = "discord.log"
