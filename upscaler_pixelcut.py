from io import BytesIO
from json import dumps
from typing import Dict, Tuple

from PIL import Image
from PIL.Image import Image as _Image
from requests import post, Response


class Upscaler:
    
    URL: str = 'https://api2.pixelcut.app/image/upscale/v1'
    
    def __init__(self, image: _Image) -> None:
        self.__image: _Image = image
    
    def __convert_image_to_binary(self) -> bytes:
        buffer: BytesIO = BytesIO()
        self.__image.save(buffer, format='JPEG')
        return buffer.getvalue()

    def __call__(self) -> _Image:
        image: bytes = self.__convert_image_to_binary()
        file: Tuple[str, bytes, str] = ('blob', image, 'image/jpeg')
        files: Dict[str, Tuple[str, bytes, str]] = {'image': file}
        params: str = dumps({'scale': 4})  # Scale must be 2 or 4.
        response: Response = post(Upscaler.URL, params=params, files=files)
        response.raise_for_status()
        image_binary: bytes = response.content
        return Image.open(BytesIO(image_binary))


if __name__ == '__main__':
    image_path: str = './image.jpg'
    image: _Image = Image.open(image_path)
    Upscaler(image)().show()
