class hp:
    platform = "gemini"
    valid_platforms = ["gemini", "ollama"]
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
    valid_obj_tasks = ["clean_text", "translate"]
