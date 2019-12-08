# -*- coding: utf-8 -*-

from odoo import _
import logging

_logger = logging.getLogger(__name__)
try:
    from PIL import ImageEnhance ,Image
    import numpy as np
    import cv2
except ImportError:
    _logger.error(_('Odoo module e2yun_cards_ocr depends on the opencv-python python module.'))


class Enhancer:

    def bright(self, image, brightness):
        bright_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image_bright = ImageEnhance.Contrast(bright_img).enhance(brightness)
        return cv2.cvtColor(np.array(image_bright), cv2.COLOR_RGB2BGR)


    def color(self, image, color):
        color_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image_color = ImageEnhance.Contrast(color_img).enhance(color)
        return cv2.cvtColor(np.array(image_color), cv2.COLOR_RGB2BGR)


    def contrast(self, image, contrast):
        pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image_contrast = ImageEnhance.Contrast(pil_img).enhance(contrast)
        return cv2.cvtColor(np.array(image_contrast), cv2.COLOR_RGB2BGR)


    def sharp(self, image, sharpness):
        pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        image_sharped = ImageEnhance.Sharpness(pil_img).enhance(sharpness)
        return cv2.cvtColor(np.array(image_sharped), cv2.COLOR_RGB2BGR)

    def gamma(self, image, gamma):
        gamma_table = [np.power(x / 255.0, gamma) * 255.0 for x in range(256)]
        gamma_table = np.round(np.array(gamma_table)).astype(np.uint8)

        return cv2.LUT(image,gamma_table)