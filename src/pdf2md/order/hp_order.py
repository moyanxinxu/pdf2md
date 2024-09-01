class hp:
    model_name_or_path = "hantian/layoutreader"
    bias = 30
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
    label2id = {v: k for k, v in id2label.items()}

    box_color = (0, 255, 0)
    text_color = (255, 0, 0)
    # model_name_or_path = "./model/"
