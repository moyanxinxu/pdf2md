import os
import re


class word_md_transformer:
    def __init__(self) -> None:
        pass

    def convert_word(self, word_file_path: str, md_file_path: str):
        """
        convert a word file to a markdown file
        """
        os.system(
            f"pandoc -f docx -t markdown --extract-media {os.path.dirname(word_file_path)} -o {md_file_path} {word_file_path}"
        )

        with open(md_file_path, "r+") as f:
            content = self.clean(f.read())
            f.seek(0)
            f.write(content)
            f.truncate()

    def inter_with_llm(self):
        """
        This function is not implemented yet.
        """
        ...

    def clean(self, text: str):
        """
        Clean the text, specifically handling image captions better.
        """
        text = self.clean_image_format(text)
        return text

    def clean_image_format(self, text: str):
        """
        Clean the text, specifically handling image captions better.
        """
        text = re.sub(r"{.*?}", "\n\n", text, flags=re.DOTALL)
        return text
