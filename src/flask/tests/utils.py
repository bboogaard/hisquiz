from io import BytesIO
from typing import BinaryIO

from PIL import Image


def generate_image(width: int, height: int, format='PNG') -> BinaryIO:
    img = Image.new(mode="RGB", size=(width, height), color=(0, 0, 0))
    fh = BytesIO()
    img.save(fh, format=format)
    return fh
