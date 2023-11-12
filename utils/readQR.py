import io
import cv2
# читать изображение QRCODE
import numpy as np


def readQR(file_io: io.BytesIO):
    file_data = np.frombuffer(file_io.read(), dtype=np.uint8)

    # Декодирование изображения с использованием OpenCV
    img = cv2.imdecode(file_data, cv2.IMREAD_COLOR)

    # Создание объекта детектора QR-кода
    qr_code_detector = cv2.QRCodeDetector()

    # Обнаружение QR-кода и получение его содержимого
    retval, points, straight_qrcode = qr_code_detector.detectAndDecode(img)
    if retval:
        return retval
    else:
        return None
