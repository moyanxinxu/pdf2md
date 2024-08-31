import os
from pathlib import Path

import numpy as np
from tqdm import tqdm

from .hp_pdf2md import hp
from .ocr.ocr_imgbyimg import ocr_model
from .order.boxes2order import LayoutLmForReadingOrder, image_layout_detector
from .others.pdf2imgs import pdf_images_transformer


class pdf_md_transformer:
    def __init__(self) -> None:
        self.pdf_img_transformer = pdf_images_transformer()
        self.image_layout_detecter = image_layout_detector()
        self.reading_order_aranger = LayoutLmForReadingOrder()
        self.ocr_model = ocr_model()

    def retrun_md(self, md_path=hp.md_path, is_save=False):
        """
        append the ocred text to a list.
        """

        txt_list = []
        types, clips = self.types, self.clips
        with open(md_path, "w") as md:
            for type, clip in zip(types, clips):
                if type not in ("table", "figure"):
                    text, _ = self.ocr_model.predict(clip)
                    if text == []:
                        print(f"OCR failed.")
                    else:
                        for t in text:
                            txt_list.append(f"{t}\n\n")
                            if is_save:
                                md.write(f"{t}\n\n")
                else:
                    txt_list.append(
                        f"![{type}](./data/clips/{hp.clips_saved_path})\n\n"
                    )
                    if is_save:
                        md.write(f"![{type}](./data/clips/{hp.clips_saved_path})\n\n")
        if is_save:
            print(f"Markdown file saved at {hp.md_path}")
        else:
            return txt_list

    def clean(self, text: str):
        """
        not implemented yet
        """
        ...

    def predict(self, pdf_path, page_num=None):
        """
        predict the text in pdf
        """
        clips, types, boxes = [], [], []
        images = self.pdf_img_transformer.split_pdf(pdf_path)
        for img in tqdm(images[:page_num], colour="green"):
            obj_types, obj_boxes, _ = self.image_layout_detecter.predict(img)
            obj_orders = self.reading_order_aranger.predict(obj_boxes)
            # arange the objects
            aranged_types = np.array(obj_types)[obj_orders].tolist()
            aranged_boxes = np.array(obj_boxes)[obj_orders].tolist()
            # aranged_scores = np.array(obj_scores)[obj_orders].tolist()

            for type, box in zip(aranged_types, aranged_boxes):
                clip = img[box[1] : box[3], box[0] : box[2]]
                clips.append(clip)
                types.append(type)
        self.types = types
        self.clips = clips
        return types, clips
