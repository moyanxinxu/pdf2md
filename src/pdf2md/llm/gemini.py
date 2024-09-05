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

        # add transport="rest" to fix the proxy and region error
        genai.configure(api_key=self.api_key, transport="rest")
        if self.is_model_valid(model_name):
            return genai.GenerativeModel(model_name)
        else:
            raise ValueError(f"invalid model name, select one of {self.valid_models}")

    def get_prompt(self, task_type, **kwargs):
        """
        Get the task prompt
        - input:
            - task_type (str): the type of the task
            - kwargs (dict): the task arguments
        - return:
            - prompt (str): the task prompt
        """
        if task_type == "clean_text":
            obj_type = kwargs.get("obj_type", None)
            if obj_type == "text":
                prompt = hp.text_promp
            elif obj_type == "title":
                prompt = hp.title_prompt
            elif obj_type == "figure_caption":
                prompt = hp.figure_caption_prompt
            elif obj_type == "table_caption":
                prompt = hp.table_caption_prompt
            elif obj_type == "header":
                prompt = hp.header_prompt
            elif obj_type == "footer":
                prompt = hp.footer_prompt
            elif obj_type == "reference":
                prompt = hp.reference_prompt
            elif obj_type == "equation":
                prompt = hp.equation_prompt
            else:
                prompt = ""
        elif task_type == "translate":
            current_language = kwargs.get("current_language", None)
            target_language = kwargs.get("target_language", None)

            con1 = current_language != target_language
            con2 = current_language != None and target_language != None

            if con1 and con2:
                prompt = hp.translate_prompt.format(
                    current_language=current_language, target_language=target_language
                )
        else:
            raise ValueError(f"invalid task_type, select one of {hp.valid_obj_tasks}")
        return prompt

    def chat(self, text):
        """
        chat with the llm model
        - inputs:
            - text (str): the text to chat with model
        - return:
            - text (str): the response from the model with markdown
        """

        text = self.model.generate_content(text)
        text = self.to_markdown(text.text)
        return text
