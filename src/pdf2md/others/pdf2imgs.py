import os

import fitz
import numpy as np

from .hp_pdf2imgs import hp


class pdf_images_transformer:
    """
    class to transform pdf to images and images to pdf
    """

    def __init__(
        self,
        zoom_x=hp.zoom_x,
        zoom_y=hp.zoom_y,
        images_saved_path=hp.images_saved_path,
    ):
        self.zoom_x = zoom_x
        self.zoom_y = zoom_y
        self.images = []
        self.images_saved_path = images_saved_path

    def split_pdf(self, pdf_path, zoom_x=2, zoom_y=2):
        """
        method to split pdf into images
        """
        images = []
        with fitz.open(pdf_path) as pdf:
            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                image = page.get_pixmap(matrix=fitz.Matrix(zoom_x, zoom_y))
                image = np.frombuffer(image.samples, dtype=np.uint8).reshape(
                    image.h, image.w, image.n
                )
                image = np.array(image)
                image = np.ascontiguousarray(image[..., [2, 1, 0]])
                images.append(image)
        self.images = images
        return images

    def save_images(self, images, images_saved_path):
        """
        method to save images splited form pdf.
        """
        if len(self.images) != 0:
            self.clean_images_saved_path(images_saved_path)
            for idx, image in enumerate(images):
                image.save(images_saved_path + f"{idx}.png")
        else:
            raise ValueError("No images found to save.")

    def clean_images_saved_path(self, path):
        """
        method to clean images saved path
        """
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                os.remove(file_path)

    def images2pdf(self):
        """
        method to convert images to pdf
        """
        ...
