from PIL import Image
import pytesseract
import cv2
import os
from urllib.request import urlopen
import numpy as np

pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'


def getText(url):
    # загрузить образ и преобразовать его в оттенки серого
    try:
        req = urlopen(url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        image = cv2.imdecode(arr, -1)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        result = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        # сохраним временную картинку в оттенках серого, чтобы можно было применить к ней OCR
        filename = "{}.png".format(os.getpid())
        cv2.imwrite(filename, result)
        # загрузка изображения в виде объекта image Pillow, применение OCR, а затем удаление временного файла
        text = pytesseract.image_to_string(Image.open(filename))
        os.remove(filename)
        return text
    except:
        return "OCR Error"
