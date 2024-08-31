class hp:
    model = "gemma:7b"
    prompt = "The following text is part of the result after PDF OCR. The text may have been a paragraph, but there may be incorrect line breaks or writing errors. Please try to restore the original text. The original text starts with </begin>:"
    stream = False
    api = "http://localhost:11434/api/chat"
