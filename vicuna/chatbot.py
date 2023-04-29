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

    def respond_to_message(self, convo_id: str, message: str) -> Optional[str]:
        """Adds given message to convo and generates a response"""
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
        # leave the bot's message blank for now
        convo.append_message(convo.roles[1], None)

        prompt = convo.get_prompt()
        params = {
            "model": Config.model_path,
            "prompt": prompt,
            "temperature": Config.temperature,
            "max_new_tokens": Config.max_new_tokens,
            # "stop": None,
            # "stop_ids": [2],
        }
        output_stream = generate_stream(
            model=self.model,
            tokenizer=self.tokenizer,
            params=params,
            device=Config.device,
            context_len=Config.context_len,
        )

        # keep generating till done
        for outputs in output_stream:
            pass
        # the final message will be final output - prompt
        l_prompt = len(prompt.replace(convo.sep2, " "))
        msg = outputs[l_prompt:].strip()
        # modify the last message in history to include the generated msg
        convo.messages[-1][-1] = msg

        self.responses_to_generate -= 1

        return msg

    def clear_convo(self, convo_id: str):
        self.convos.pop(convo_id, None)
