import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def generate_qr_code_image(data: str, filename='qr.png'):
    img = qrcode.make(data)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=filename)
