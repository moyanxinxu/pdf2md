import os

from pdf2md import pdf_md_transformer
from word2md import word_md_transformer


def main(pdf_path, md_path):
    pdf_path = os.path.abspath(pdf_path)
    model = pdf_md_transformer()
    types, clips = model.predict(pdf_path)
    text = model.retrun_md(is_save=True)


if __name__ == "__main__":
    main("./pdf2md/data/pdfs/attention-is-all-your-need.pdf", "./result.md")
