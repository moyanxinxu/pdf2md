# pip install -q -U google-generativeai
import google.generativeai as genai

from .hp_api import hp


class gemini_text_formater:
    def __init__(self) -> None:
        self.platform = "gemini"
        self.stream = hp.gemini_stream
        self.api_key = hp.gemini_api_key
        self.model_name = hp.gemini_model_name
        self.model = self.get_model(self.model_name)

    def to_markdown(self, text):
        # copyed from https://ai.google.dev/gemini-api/docs/get-started/tutorial?lang=python
        """
        convert the text to markdown
        - input:
            - text (str): the text to be converted
        - return:
            - text (str): the converted text with markdown
        """
        text = text.replace("•", "  *")
        return text

    def is_model_valid(self, model_name):
        """
        check if the model name is valid
        - input:
            - model_name (str): the name of the model
        - return:
            - bool: True if the model is valid, False otherwise
        """
        valid_models = [
            m.name.replace("models/", "")
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]

        self.valid_models = valid_models

        if model_name in valid_models:
            return True
        else:
            return False

    def get_model(self, model_name):
        """
        Get the model object

        - input:
            - model_name (str): the name of the model
        - return:
            - genai.GenerativeModel: the model object
        """
        genai.configure(api_key=self.api_key)
        if self.is_model_valid(model_name):
            return genai.GenerativeModel(model_name)
        else:
            raise ValueError(f"invalid model name, select one of {self.valid_models}")

    def clean(self, text):
        """
        Clean the text
        - inputs:
            - text (str): the text to be cleaned
        - return:
            - text (str): the cleaned text
        """

        text = self.model.generate_content(text)
        text = self.to_markdown(text.text)
        return text
