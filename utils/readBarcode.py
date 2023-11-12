import io
import cv2
import numpy as np



def readBarcode(file_io: io.BytesIO):
    file_data = np.frombuffer(file_io.read(), dtype=np.uint8)
    # Декодирование изображения с использованием OpenCV
    img = cv2.imdecode(file_data, cv2.IMREAD_COLOR)

    # Создание объекта детектора штрихкода
    barcode_detector = cv2.barcode.BarcodeDetector()

    # Обнаружение штрихкода и получение его содержимого
    retval, points, straight_code = barcode_detector.detectAndDecode(img)

    if retval:
        return retval
    else:
        return None
