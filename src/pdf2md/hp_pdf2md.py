class hp:
    pdf_path = "./data/pdfs/attention-is-all-your-need.pdf"
    images_saved_path = "./data/images/"
    clips_saved_path = "./data/clips/"
    id2label = {
        0: "text",
        1: "title",
        2: "figure",
        3: "figure caption",
        4: "table",
        5: "table caption",
        6: "header",
        7: "footer",
        8: "reference",
        9: "equation",
    }

    label2id = {
        "text": 0,
        "title": 1,
        "figure": 2,
        "figure caption": 3,
        "table": 4,
        "table caption": 5,
        "header": 6,
        "footer": 7,
        "reference": 8,
        "equation": 9,
    }
    comment_prompt = "If you are a paper writing assistant, When answering, do not add anything other than the original content."
    title_prompt = (
        comment_prompt + "the following text is a title, please correct it:\n ##"
    )
    figure_caption_prompt = (
        comment_prompt + "the following text is a figure caption, please correct it:\n"
    )
    table_caption_prompt = (
        comment_prompt + "the following text is a table caption, please correct it:\n"
    )
    header_prompt = (
        comment_prompt + "the following text is a header, please correct it:\n"
    )
    footer_prompt = (
        comment_prompt + "the following text is a footer, please correct it:\n"
    )
    reference_prompt = (
        comment_prompt + "the following text is a reference, please correct it:\n"
    )
    equation_prompt = (
        comment_prompt
        + "the following text is an equation, please correct it by latex or markdown:\n"
    )

    text_promp = comment_prompt + "the following text is a text, please correct it:\n"
