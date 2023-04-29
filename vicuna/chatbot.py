from typing import Dict, Optional
from fastchat.serve.inference import load_model, generate_stream, compute_skip_echo_len
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
        # number of responses to messages need to generate
        self.responses_to_generate = 0

    def create_new_convo(self, convo_id: str):
        """Creates a new convo if nonexistent"""
        if self.convos.get(convo_id, None) is None:
            self.convos[convo_id] = Config.convo.copy()

    # def add_to_convo(self, convo_id: str, message: str):
    #     """Adds a message to a convo"""
    #     self.create_new_convo(convo_id)
    #     convo = self.convos[convo_id]
    #     # add message to convo obj
    #     convo.append_message(convo.roles[0], message)
    #     convo.append_message(convo.roles[1], message)
    #     self.requests_to_generate += 1

    # def generate_response(self, convo_id: str) -> Optional[str]:
    #     """Generate a response to a convo"""
    #     # don't generate response if over limit
    #     if (
    #         self.requests_to_generate > Config.requests_to_generate_limit
    #         and Config.requests_to_generate_limit != -1
    #     ):
    #         return None

    #     self.create_new_convo(convo_id)
    #     convo = self.convos[convo_id]

    #     # taken from vicuna's src code (fastchat/serve/inference.py)
    #     prompt = convo.get_prompt()
    #     params = {
    #         "model": Config.model_path,
    #         "prompt": prompt,
    #         "temperature": Config.temperature,
    #         "max_new_tokens": Config.max_new_tokens,
    #         "stop": None,
    #     }
    #     skip_echo_len = compute_skip_echo_len(Config.model_path, convo, prompt)
    #     output_stream = generate_stream(
    #         model=self.model,
    #         tokenizer=self.tokenizer,
    #         params=params,
    #         device=Config.device,
    #         context_len=Config.context_len,
    #     )
    #     pre = 0
    #     msg = ""
    #     for outputs in output_stream:
    #         outputs = outputs[skip_echo_len:].strip()
    #         outputs = outputs.split(" ")
    #         now = len(outputs) - 1
    #         if now > pre:
    #             msg += " ".join(outputs[pre:now]) + " "
    #             pre = now
    #     msg += " ".join(outputs[pre:])
    #     msg = msg.strip()
    #     if len(msg) > 2000:
    #         msg = msg[:2000]
    #     convo.messages[-1][-1] = " ".join(outputs).strip()

    #     # msg = "i'm a wip, so i schleep now"
    #     # self.add_to_convo(convo_id, msg, role=1)
    #     self.requests_to_generate -= 1
    #     return msg

    def respond_to_message(self, convo_id: str, message: str) -> Optional[str]:
        # don't generate response if over limit
        if (
            self.responses_to_generate > Config.responses_to_generate_limit
            and Config.responses_to_generate_limit != -1
        ):
            return None

        self.responses_to_generate += 1
        self.create_new_convo(convo_id)
        convo = self.convos[convo_id]

        convo.append_message(convo.roles[0], message)
        convo.append_message(convo.roles[1], None)

        prompt = convo.get_prompt()
        skip_echo_len = compute_skip_echo_len(Config.model_path, convo, prompt)
        stop_str = None
        params = {
            "model": Config.model_path,
            "prompt": prompt,
            "temperature": Config.temperature,
            "max_new_tokens": Config.max_new_tokens,
            "stop": None,
            # "stop_ids": [2],
        }
        output_stream = generate_stream(
            model=self.model,
            tokenizer=self.tokenizer,
            params=params,
            device=Config.device,
            context_len=Config.context_len,
        )

        l_prompt = len(prompt.replace(convo.sep2, " "))
        for outputs in output_stream:
            pass
        msg = outputs[l_prompt:].strip()
        convo.messages[-1][-1] = msg

        self.responses_to_generate -= 1

        return msg
