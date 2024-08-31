import os

import cv2 as cv
import numpy as np
from hp_pdf2md import hp
from ocr.ocr_imgbyimg import ocr_model
from order.boxes2order import LayoutLmForReadingOrder, image_layout_detector
from others.pdf2imgs import pdf_images_transformer


class pdf_md_transformer:
    def __init__(self) -> None:
        self.pdf_img_transformer = pdf_images_transformer()
        self.image_layout_detecter = image_layout_detector()
        self.reading_order_aranger = LayoutLmForReadingOrder()
        self.ocr_model = ocr_model()

    def sorted_ls(dir):
        if os.path.exists(hp.clips_saved_path):
            return sorted(
                os.listdir(dir),
                key=lambda x: (int(x.split("_")[0]), int(x.split("_")[1])),
            )
        else:
            raise ValueError("No clips saved, please run predict first")

    def save_md(self, md_path):
        with open(md_path, "w") as md:
            for img_path in self.sorted_ls(hp.clips_saved_path):
                page_num, order_num_in_page, box_type_in_page = img_path.split("_")[:3]
                if box_type_in_page not in ("table", "figure"):
                    text, _ = self.ocr_model.prdict(
                        os.path.join(hp.clips_saved_path, img_path)
                    )
                    if text == []:
                        print(
                            f"OCR failed on page {page_num}, order {order_num_in_page}, box type {box_type_in_page}"
                        )
                    else:
                        for t in text:
                            md.write(f"{t}\n\n")
                else:
                    md.write(f"![{box_type_in_page}](./data/clips/{img_path})\n\n")

    def clean(self, text: str):
        """
        not implemented yet
        """
        ...

    def predict(self, pdf_path):
        images = self.pdf_img_transformer.split_pdf(pdf_path)
        self.pdf_img_transformer.save_images(images, hp.images_saved_path)
        self.pdf_img_transformer.clean_images_saved_path(hp.clips_saved_path)
        for img_path in os.listdir(hp.images_saved_path):
            img_idx = img_path.split(".")[0]
            img_path = os.path.join(hp.images_saved_path, img_path)
            obj_types, obj_boxes, obj_scores = self.image_layout_detecter.predict(
                img_path
            )
            obj_orders = self.reading_order_aranger.predict(obj_boxes)
            # arange the objects
            aranged_types = np.array(obj_types)[obj_orders].tolist()
            aranged_boxes = np.array(obj_boxes)[obj_orders].tolist()
            aranged_scores = np.array(obj_scores)[obj_orders].tolist()

            for idx, type, box in zip(obj_orders, aranged_types, aranged_boxes):
                img = cv.imread(img_path)
                clip = img[box[1] : box[3], box[0] : box[2]]
                cv.imwrite(
                    os.path.join(hp.clips_saved_path, f"{img_idx}_{idx}_{type}_.png"),
                    clip,
                )
