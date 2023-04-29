from typing import Dict
from fastchat.serve.inference import load_model, generate_stream
from fastchat.conversation import Conversation, SeparatorStyle

from config import Config


class JazzyChatbot:
    def __init__(self) -> None:
        # load model from config
        self.model, self.tokenizer = load_model(
            model_path=Config.model_path,
            device=Config.device,
            num_gpus=Config.num_gpus,
            max_gpu_memory=Config.max_gpu_memory,
            load_8bit=Config.load_8bit,
            debug=Config.debug,
        )

        # stores all the convos for one chatbot as { id: Conversation }
        self.convos: Dict[str, Conversation] = {}
        # number of requests to generate response
        self.requests_to_generate = 0

    def create_new_convo(self, convo_id: str):
        """Creates a new convo if nonexistent"""
        if self.convos.get(convo_id, None) is None:
            self.convos[convo_id] = Config.convo.copy()

    def add_to_convo(self, convo_id: str, message: str, role: int):
        """Adds a message to a convo"""
        self.create_new_convo(convo_id)
        # check role index
        if role < 0 or role >= len(self.convos[convo_id].roles):
            raise ValueError("role out of index")
        # add message to convo obj
        self.convos[convo_id].append_message(self.convos[convo_id].roles[role], message)

    def generate_response(self, convo_id: str) -> str | None:
        """Generate a response to a convo"""
        # don't generate response if over limit
        if (
            self.requests_to_generate > Config.requests_to_generate_limit
            and Config.requests_to_generate_limit != -1
        ):
            return None
        self.create_new_convo(convo_id)
        convo = self.convos[convo_id]

        # taken from vicuna's src code (fastchat/serve/inference.py)
        prompt = convo.get_prompt()
        stop_str = (
            convo.sep
            if convo.sep_style in [SeparatorStyle.SINGLE, SeparatorStyle.BAIZE]
            else None
        )
        params = {
            "model": Config.model_path,
            "prompt": prompt,
            "temperature": Config.temperature,
            "max_new_tokens": Config.max_new_tokens,
            "stop": stop_str,
        }
        output_stream = generate_stream(
            self.model, self.tokenizer, params, Config.device
        )
        msg = " ".join(output_stream).strip()

        msg = "i'm a wip, so i schleep now"

        self.add_to_convo(convo_id, msg, role=1)
        return msg
