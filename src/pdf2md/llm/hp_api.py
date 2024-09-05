class hp:
    prompt = "The following text is extracted by OCR maybe exist a lot of mistakes, please correct these texts, only one answer, keep meaning :\n\n"
    ollama_model_name = "gemma:2b"
    ollama_stream = False
    ollama_api = "http://localhost:11434"

    gemini_model_name = "gemini-1.5-flash"
    gemini_api_key = "AIzaSyAPFFuJ5CUjKkMOscRashynokshj8gGyrM"
    gemini_stream = False

    translate_prompt = "the following text is in {current_language}, please translate it to {target_language}"
    commen_prompt = "If you are a paper writing assistant, When answering, do not add anything other than the original content."
    title_prompt = (
        commen_prompt + "the following text is a title, please correct it:\n ##"
    )
    figure_caption_prompt = (
        commen_prompt + "the following text is a figure caption, please correct it:\n"
    )
    table_caption_prompt = (
        commen_prompt + "the following text is a table caption, please correct it:\n"
    )
    header_prompt = (
        commen_prompt + "the following text is a header, please correct it:\n"
    )
    footer_prompt = (
        commen_prompt + "the following text is a footer, please correct it:\n"
    )
    reference_prompt = (
        commen_prompt + "the following text is a reference, please correct it:\n"
    )
    equation_prompt = (
        commen_prompt
        + "the following text is an equation, please correct it by latex or markdown:\n"
    )

    text_promp = (
        commen_prompt
        + "the following text is a text from **same paragraph**, please correct it:\n"
    )
