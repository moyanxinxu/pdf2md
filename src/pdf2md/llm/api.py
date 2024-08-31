import requests

from .hp_api import hp


class text_formater:
    def __init__(self) -> None:
        self.llm = hp.model
        self.url = hp.api

    def header(self, text: str):
        return {
            "model": self.llm,
            "messages": [
                {
                    "role": "user",
                    "content": hp.prompt + text,
                },
            ],
            "stream": hp.stream,
        }

    def post(self, text: str):
        response = requests.post(self.url, json=self.header(text))
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"request failed: {response.status_code}"
