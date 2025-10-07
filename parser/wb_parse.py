import asyncio
import re

import aiohttp

from core.enums import Platform
from parser.base_parse import BaseParser


class WbParser(BaseParser):

    def __init__(self):
        """
        初始化
        """
        super().__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0",
        }

    async def get_platform(self) -> Platform:
        return Platform.WEI_BO

    async def is_me(self, url: str) -> bool:
        """
        判断是否是该平台
        :param url:
        :return:
        """
        pattern = re.compile(r'https?://(?:[a-zA-Z0-9-]+\.)?weibo\.com/[^"\'\s]+')
        return bool(re.match(pattern, url))

    async def parse(self, url: str) -> list[str]:
        sub = self.get_sub_cookie(url)
        self.headers["cookie"] = f'SUB={sub}'

        self.headers['Referer'] = url

        url = f'https://weibo.com/ajax/statuses/show?id={url.split('/')[-1]}&locale=zh-CN&isGetLongText=true'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers = self.headers) as response:
                resp_json = await response.json()

                if 'mix_media_info' in resp_json:

                    media_list = resp_json.get('mix_media_info').get('items')
                    result = []
                    for media in media_list:
                        if media.get('type') == 'video':
                            result.append(
                                media.get('data').get('media_info').get('playback_list')[0].get('play_info').get('url'))
                            # cdn好像有鉴权
                        else:
                            result.append(media.get('data').get('original').get('url'))

                    return result
                else:
                    return [resp_json.get('page_info').get('media_info').get('playback_list')[0].get('play_info').get(
                        'url')]

    def get_sub_cookie(self, target_url: str) -> str:
        import requests

        url = "https://login.sina.com.cn/visitor/visitor"

        params = {
            'a': 'crossdomain',
            's': '_2AkMfuECSf8NxqwFRmvwVy2PlbYt2zw3EieKp5LFJJRMxHRl-yT9xqmUBtRB6NDhufdGMIaCz-AheLFGkpRH4YzKuw1XL',
            'sp': '0033WrSXqPxfM72-Ws9jqgMF55529P9D9Who4u-457l5Rr6.YMfWR96A',
            'from': 'weibo',
            'entry': 'miniblog',
            'url': target_url
        }

        response = requests.get(url, params = params)

        set_cookie = response.history[0].headers['Set-Cookie']
        return set_cookie[set_cookie.index("=") + 1: set_cookie.index(";")]


async def main():
    wb_parser = WbParser()

    resp = await wb_parser.parse("https://weibo.com/1791027450/5218774761867334")
    # resp = await wb_parser.parse("https://weibo.com/5115885691/5214191268664426")
    print(resp)
    print(len(resp))


if __name__ == '__main__':
    asyncio.run(main())  # ✅ 正确执行
