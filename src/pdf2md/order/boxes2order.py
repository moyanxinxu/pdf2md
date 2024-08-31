import cv2 as cv
import numpy as np
from paddleocr import PPStructure
from transformers import LayoutLMv3ForTokenClassification

from .aux import boxes2inputs, parse_logits, prepare_inputs
from .hp_order import hp


class image_layout_detector:
    """
    a class to detect the layout of an image
    """

    def __init__(self):
        self.table_engine = PPStructure(
            show_log=False,
            image_orientation=True,
            ocr=False,
            layout=True,
        )

    def predict(self, img):
        """
        detect the layout of an image

        - inputs:
            - img: cv.Mat, the image to be detected
        - return
            - obj_types: the type of the detected objects in the image
            - obj_boxes: the bounding boxes of the detected objects in the image
            - obj_scores: the confidence scores of the detected objects in the image
        """
        result = self.table_engine(img)
        obj_types = []
        obj_boxes = []
        obj_scores = []

        for obj in result:
            obj_types.append(obj["type"])
            obj_boxes.append(obj["bbox"])
            obj_scores.append(obj["score"])
        return obj_types, obj_boxes, obj_scores


class LayoutLmForReadingOrder:
    """
    A class to predict the reading order of a list of boxes
    """

    def __init__(self, model_name_or_path=hp.model_name_or_path):
        self.model = LayoutLMv3ForTokenClassification.from_pretrained(
            model_name_or_path,
            use_safetensors=True,
            local_files_only=True,
        )

    def scale(self, boxes):
        """
        Args:
            boxes: list of [xmin, ymin, xmax, ymax], bboxes of spans
        Returns:
            boxes: list of [xmin, ymin, xmax, ymax], bboxes of spans, range from 0 to 1000
        """
        # boxes's format [[...], ...]
        # scale to 0-1000
        array = np.array(boxes)
        maximum = np.max(array)
        minimum = np.min(array)
        array = (array - minimum) / (maximum - minimum) * 999
        array = array.astype(int)
        return array.tolist()

    def predict(self, boxes):
        """
        Args:
            boxes: list of [xmin, ymin, xmax, ymax] after scaled, bboxes of spans, range from 0 to 1000
        Returns:
            orders: list of int, the reading order of the boxes
        """
        inputs = self.scale(boxes)
        inputs = boxes2inputs(inputs)
        inputs = prepare_inputs(inputs, self.model)
        logits = self.model(**inputs).logits.cpu().detach().squeeze(0)
        orders = parse_logits(logits, len(boxes))
        return orders
