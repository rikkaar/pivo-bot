import io
from qrcode.main import QRCode
from qrcode.constants import ERROR_CORRECT_L
from aiogram.types import BufferedInputFile

# Id для генерации уникального названия и data - то, что будет внутри QR-кода


def generateQrCode(data) -> BufferedInputFile:
    qr = QRCode(
        error_correction=ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)
    return BufferedInputFile(
        img_io.read(),
        'filename'
    )
