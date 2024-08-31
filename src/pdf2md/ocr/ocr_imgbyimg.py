from paddleocr import PaddleOCR


class ocr_model:
    def __init__(self):
        self.model = PaddleOCR(use_angle_cls=True, lang="en", use_mp=True)

    def prdict(self, img_path):
        result = self.model.ocr(img_path, cls=True)[0]
        texts, scores = [], []
        if result is None:
            pass
        else:
            for item in result:
                text, score = item[-1]
                texts.append(text)
                scores.append(score)
        return texts, scores
