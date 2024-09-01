import os

import ollama

from .hp_api import hp


class text_formater:
    def __init__(self) -> None:
        self.model_name = hp.model
        self.stream = hp.stream
        self.llm = self.host(hp.api)

    def host(self, host_address):
        return ollama.Client(host=host_address)

    def clean(self, text):
        return self.llm.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": hp.prompt + " ".join(text).strip(),
                },
            ],
            stream=self.stream,
        )["message"]["content"]
