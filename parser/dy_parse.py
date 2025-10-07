# //div[contains(@class, "focusPanel")]//img[contains(@src, "p3-pc-sign.douyinpic.com/tos-cn-i-") and contains(@src, "x-expir")]/following-sibling::div[1]//img

import asyncio
import re
from urllib.parse import urlparse

import aiohttp

from core.enums import Platform
from parser.base_parse import BaseParser


class DyParser(BaseParser):

    def __init__(self):
        """
        初始化
        """
        super().__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1 Edg/140.0.0.0"
        }

    async def get_platform(self) -> Platform:
        return Platform.DOU_YIN

    async def is_me(self, url: str) -> bool:
        """
        判断是否是该平台
        :param url:
        :return:
        """
        pattern = re.compile(r'https?://(?:[a-zA-Z0-9-]+\.)?douyin\.com/[^"\'\s]+')
        return bool(re.match(pattern, url))

    async def parse(self, url: str) -> list[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers = self.headers) as response:
                resp = await response.text()

                if "video-container" in resp:
                    return self.parse_video(resp)
                return self.parse_image(resp)

    def parse_image(self, resp: str) -> list[str]:

        resp = resp.replace(r"\u002F", "/")
        pattern = re.compile(r'https?:\/\/p[0-9]+-sign\.douyinpic\.com\/tos-cn-i-.+?\/[^"\s]+', re.S)
        urls = re.findall(pattern, resp)

        # 会有很多地址，exclude_keys中都是些被二次处理过后的，不要
        exclude_keys = ["tplv", "water", "shrink", "lqen", "resize"]
        seen = set()
        result = []

        for u in urls:
            # 这里会每张图片存在四张不同签名的地址，只需要其中一个就好
            if any(k in u for k in exclude_keys):
                continue
            path = urlparse(u).path
            if path in seen or path.endswith(".webp"):
                continue
            seen.add(path)
            result.append(self.handle_image_url(u))

        return result

    def parse_video(self, resp: str) -> list[str]:
        resp = resp.replace(r"\u002F", "/")
        pattern = re.compile(r'https?:\/\/sns-video-[a-z]{2,}\.xhscdn\.com\/[^"\'\s]+', re.S)
        urls = re.findall(pattern, resp)
        if urls:
            # 有水印 http://sns-video-qc.xhscdn.com/stream/79/110/259/01e8e3cdf1e8b9b30103700399b9dcd5ae_259.mp4?sign=0b0a9dbfb471923283af843b05d62cdf&t=68e91596
            # 无水印 https://sns-video-hs.xhscdn.com/stream/79/110/114/01e8e3cdf1e8b9b34f03700199b9dd02af_114.mp4
            return urls[0]
        return []

    def handle_image_url(self, url):
        """
        处理错误
        :param error:
        :return:
        """
        return url.replace("/w/720/format/jpg", "/w/2560/format/jpg")


async def main():
    dy_parser = DyParser()
    resp = await dy_parser.parse("https://v.douyin.com/_EsQU01y3cQ/")
    print(resp)
    print(len(resp))


if __name__ == '__main__':
    asyncio.run(main())  # ✅ 正确执行
