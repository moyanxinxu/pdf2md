import ollama

from .hp_api import hp


class ollama_text_formater:
    def __init__(self) -> None:
        """
        Initialize the text_formater class
        """
        self.platform = "ollama"
        self.model_name = hp.ollama_model_name
        self.stream = hp.ollama_stream
        self.llm = self.host(hp.ollama_api)

    def host(self, host_address):
        """
        Connect to the API host
        - inputs:
            - host_address (str): the address of the API host
        - return:
            - ollama.Client: the client object
        """
        return ollama.Client(host=host_address)

    def clean(self, text):
        """
        Clean the text
        - inputs:
            - text (str): the text to be cleaned
        - return:
            - text (str): the cleaned text
        """
        return self.llm.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": text.strip(),
                },
            ],
            stream=self.stream,
        )["message"]["content"]
