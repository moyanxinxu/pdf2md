import numpy as np
from tqdm import tqdm

from .hp_pdf2md import hp
from .llm import gemini_text_formater, ollama_text_formater
from .ocr.ocr_imgbyimg import ocr_model
from .order.boxes2order import LayoutLmForReadingOrder, image_layout_detector
from .others.pdf2imgs import pdf_images_transformer


class pdf_md_transformer:
    def __init__(self) -> None:
        self.text_formater = self.get_model(hp.platform)
        self.load_models()

    def offload_models(self):
        """
        Due to the size of the text_formater, this function try offload other model.
        """
        del self.pdf_img_transformer
        del self.image_layout_detecter
        del self.reading_order_aranger

    def load_models(self):
        """
        After llm cleaned the text, the method will load model again.
        """
        self.pdf_img_transformer = pdf_images_transformer()
        self.image_layout_detecter = image_layout_detector()
        self.reading_order_aranger = LayoutLmForReadingOrder()
        self.ocr_model = ocr_model()

    def get_model(self, platform):
        """
        select the text formater model

        - input:
            - platform (str), the platform of the model
        - return:
            - text_formater: the text formater model
        """
        if platform == "gemini":
            return gemini_text_formater()
        elif platform == "ollama":
            return ollama_text_formater()
        else:
            raise ValueError(f"invalid platform, selcet one of {hp.valid_platforms}")

    def clean_text(self, types, clips):
        """
        append the ocred text to a list.
        """
        txt_list = []
        for type, clip in tqdm(zip(types, clips), total=len(types), colour="green"):
            if type not in ("table", "figure"):
                text, _ = self.ocr_model.predict(clip)
                if text == []:
                    pass
                else:
                    prompt = self.text_formater.get_prompt(
                        task_type="clean_text",
                        obj_type=type,
                    )
                    pull = self.text_formater.chat(prompt + "\n".join(text).strip())
                    txt_list.append(pull)
            else:
                img_md = f"![{type}]({hp.clips_saved_path})\n\n"
                txt_list.append(img_md)
        self.load_models()
        return txt_list

    def translate(self, current_language, target_language, text):
        """
        translate the text
        - input:
            - current_language: str, the current language
            - target_language: str, the target language
            - text: str, the text to be translated
        - return:
            - pull: str, the translated text
        """
        prompt = self.text_formater.get_prompt(
            task_type="translate",
            current_language=current_language,
            target_language=target_language,
        )
        pull = self.text_formater.chat(prompt + text)
        return pull

    def predict(self, pdf_path, page_num=None):
        """
        predict the text in pdf

        - inputs:
            - pdf_path: str, the path of the pdf file
            - page_num: int, the number of pages to be predicted
        - return:
            - types: list of str, the types of the objects
            - clips: list of cv.Mat, the objects
        """
        clips, types, _ = [], [], []
        images = self.pdf_img_transformer.split_pdf(pdf_path)
        for img in tqdm(images[:page_num], colour="green"):
            obj_types, obj_boxes, _ = self.image_layout_detecter.predict(img)
            obj_orders = self.reading_order_aranger.predict(obj_boxes)
            # arange the objects
            aranged_types = np.array(obj_types)[obj_orders].tolist()
            aranged_boxes = np.array(obj_boxes)[obj_orders].tolist()
            # aranged_scores = np.array(obj_scores)[obj_orders].tolist()

            for type, box in zip(aranged_types, aranged_boxes):
                clip = np.zeros_like(img)

                # TODO 非检测区域都设置为0,期望这样做能够提高ocr准确率,实际效果目测是提升了很多.
                clip[box[1] : box[3], box[0] : box[2]] = img[
                    box[1] : box[3], box[0] : box[2]
                ]
                clips.append(clip)
                types.append(type)
        self.types = types
        self.clips = clips
        self.offload_models()
        return types, clips
