import os

from pdf2md import pdf_md_transformer
from word2md import word_md_transformer


def main(pdf_path, md_path):
    model = pdf_md_transformer()
    pdf_path = os.path.abspath(pdf_path)
    types, clips = model.predict(pdf_path, page_num=2)
    text_list = model.retrun_md()
    with open("./result.md", "w") as f:
        print(text_list, file=f)


if __name__ == "__main__":
    main("./pdf2md/data/pdfs/attention-is-all-your-need.pdf", "./result.md")
