from hashlib import md5
from io import BytesIO
from random import random
from typing import Dict

from fake_useragent import FakeUserAgent
from PIL import Image
from PIL.Image import Image as _Image
from requests import Response, get
from requests_html import HTMLSession


class Upscaler:
    
    TRY_IT: str = 'tryit-{}-{}'
    API_URL: str = 'https://api.deepai.org/api/torch-srgan'
    URL: str = 'https://deepai.org/machine-learning-model/torch-srgan'

    def __init__(self, image: _Image) -> None:
        bytesio: BytesIO = BytesIO()
        image.save(bytesio, format='PNG')
        self.__image_bytes: bytes = bytesio.getvalue()

    def __generate_random_string(self) -> str:
        return str(round(1e11 * random()))

    def __md5_encode(self, string: str) -> str:
        return md5(string.encode('utf-8')).hexdigest()[::-1]

    def __generate_user_agent(self) -> str:
        return FakeUserAgent().random

    def __get_image_url(self, user_agent: str, api_key: str) -> str:
        headers: Dict[str, str] = {
            'user-agent': user_agent, 'api-key': api_key}
        file: Dict[str, bytes] = {'image': self.__image_bytes}
        session: HTMLSession = HTMLSession()
        session.get(Upscaler.URL)  # Prevent finished trial error.
        response: Response = session.post(
            Upscaler.API_URL, headers=headers, files=file)
        response.raise_for_status()
        return response.json()['output_url']

    def __download_upscale_image(self, url: str) -> _Image:
        response: Response = get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))

    def __call__(self) -> _Image:
        user_agent: str = self.__generate_user_agent()
        random_string: str = self.__generate_random_string()
        first_hash: str = self.__md5_encode(user_agent + random_string + 'x')
        second_hash: str = self.__md5_encode(user_agent + first_hash)
        final_hash: str = self.__md5_encode(user_agent + second_hash)
        api_key: str = Upscaler.TRY_IT.format(random_string, final_hash)
        image_url: str = self.__get_image_url(user_agent, api_key)
        return self.__download_upscale_image(image_url)


if __name__ == '__main__':
    image_path: str = './image.jpg'
    image: _Image = Image.open(image_path)
    Upscaler(image)().show()
