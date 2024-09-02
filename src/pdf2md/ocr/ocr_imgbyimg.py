import cv2 as cv
from paddleocr import PaddleOCR

from .hp_ocr import hp


class ocr_model:
    def __init__(self):
        """
        Initialize the OCR model
        """
        self.model = PaddleOCR(use_angle_cls=True, lang="en", use_mp=True)

    def aug(self, img):
        """
        augment the image, inclueing binarization utile now.

        - inputs:
            - img: cv.Mat, the image to be augmented
        - return:
            - img: cv.Mat, the augmented image
        """
        if len(img.shape) == 3:
            img = cv.cvtColor(img.copy(), cv.COLOR_BGR2GRAY)
        _, binary_img = cv.threshold(img, hp.threshold, 255, cv.THRESH_BINARY)
        return binary_img

    def predict(self, img):
        """
        extract text from image.

        - inputs:
            - img: cv.Mat, the image to be extracted
        - return:
            - texts: list of str, the extracted texts
            - scores: list of float, the confidence scores of the extracted texts
        """

        img = self.aug(img)
        result = self.model.ocr(img, cls=True)[0]
        texts, scores = [], []
        if result is None:
            pass
        else:
            for item in result:
                text, score = item[-1]
                texts.append(text)
                scores.append(score)
        return texts, scores
