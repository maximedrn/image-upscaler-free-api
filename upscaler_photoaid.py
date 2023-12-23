from base64 import b64decode, b64encode
from io import BytesIO
from json import dumps
from random import randint
from time import sleep
from typing import Dict

from PIL import Image
from PIL.Image import Image as _Image
from requests import Response
from requests_html import HTMLSession


class Upscaler:
    
    TOKEN_URL: str = 'https://photoaid.com/en/tools/api/tools/token'
    UPLOAD_URL: str = 'https://photoaid.com/en/tools/api/tools/upload'
    UPLOAD_REQUEST_URL: str = '/ai-image-enlarger/upload'
    RESULT_URL: str = 'https://photoaid.com/en/tools/api/tools/result'
    RESULT_REQUEST_URL: str = '/ai-image-enlarger/result'
    
    def __init__(self, image: _Image) -> None:
        self.__image: _Image = image
        self.__session: HTMLSession = HTMLSession()
    
    def __image_to_base64(self) -> str:
        image_binary: BytesIO = BytesIO()
        self.__image.save(image_binary, format='JPEG')
        return b64encode(image_binary.getvalue()).decode('utf-8')

    def __generate_token(self) -> str:
        response: Response = self.__session.post(Upscaler.TOKEN_URL)
        response.raise_for_status()
        return response.json()['token']
    
    def __format_cookies(self, token: str) -> Dict[str, str]:
        return {'uuidtoken2': token}
    
    def __format_upload_data(self, token: str, image: str) -> str:
        data: Dict[str, str] = {
            'token': token, 'base64': image,
            'reqURL': Upscaler.UPLOAD_REQUEST_URL}
        return dumps(data)

    def __upload_image_file(self, token: str, image: str) -> str:
        data: str = self.__format_upload_data(token, image)
        cookies: Dict[str, str] = self.__format_cookies(token)
        response: Response = self.__session.post(
            Upscaler.UPLOAD_URL, data=data, cookies=cookies)
        response.raise_for_status()
        return response.json()['request_id']
    
    def __format_result_data(self, request_id: str) -> str:
        data: Dict[str, str] = {
            'request_id': request_id, 'reqURL': Upscaler.RESULT_REQUEST_URL}
        return dumps(data)
    
    def __retrieve_final_image(self, request_id: str, token: str) -> str:
        data: str = self.__format_result_data(request_id)
        cookies: Dict[str, str] = self.__format_cookies(token)
        final_image: str = ''  # Prevent outbound error.
        while not final_image:
            response: Response = self.__session.post(
                Upscaler.RESULT_URL, data=data, cookies=cookies)
            response.raise_for_status()
            final_image = response.json()['result']
            if not final_image:  # Wait before asking again the server.
                sleep(randint(1, 5))
        return final_image

    def __base64_to_image(self, image: str) -> _Image:
        if image.startswith('data:image'):
            image = image.split(',', 1)[1]
        image_bytes: bytes = b64decode(image)
        image_buffer: BytesIO = BytesIO(image_bytes)
        return Image.open(image_buffer)

    def __call__(self) -> _Image:
        image: str = self.__image_to_base64()
        token: str = self.__generate_token()
        request_id: str = self.__upload_image_file(token, image)
        final_image: str = self.__retrieve_final_image(request_id, token)
        return self.__base64_to_image(final_image)


if __name__ == '__main__':
    image_path: str = './image.jpg'
    image: _Image = Image.open(image_path)
    Upscaler(image)().show()