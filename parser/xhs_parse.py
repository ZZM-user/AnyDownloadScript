import asyncio
import re

import aiohttp

from core.enums import Platform
from parser.base_parse import BaseParser


class XhsParser(BaseParser):

    def __init__(self):
        """
        初始化
        """
        super().__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1 Edg/140.0.0.0"
        }

    async def get_platform(self) -> Platform:
        return Platform.XIAO_HONG_SHU

    async def is_me(self, url: str) -> bool:
        return url.startswith("http://xhslink.com/") or url.startswith("https://xhslink.com/")

    async def parse(self, url: str) -> list[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers = self.headers) as response:
                resp = await response.text()

                if "video-container" in resp:
                    return self.parse_video(resp)
                return self.parse_image(resp)

    def parse_image(self, resp: str) -> list[str]:
        pattern = re.compile(r'https:\/\/sns-na-i[0-9]\.xhscdn\.com\/[^"\'\s]+', re.S)
        urls = re.findall(pattern, resp)
        if urls:
            # 去重 + 保证顺序
            seen = set()
            return [self.handle_image_url(u) for u in urls if not (u in seen or seen.add(u))]
        return []

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
    xhs_parser = XhsParser()
    resp = await xhs_parser.parse(
        "http://xhslink.com/o/20mA64hum20")
    print(resp)


if __name__ == '__main__':
    asyncio.run(main())  # ✅ 正确执行
