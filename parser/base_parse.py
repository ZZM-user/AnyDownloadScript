from abc import ABC, abstractmethod

from core.enums import Platform


class BaseParser(ABC):
    @abstractmethod
    async def get_platform(self) -> Platform:
        """获取当前平台"""
        pass

    @abstractmethod
    async def is_me(self, url: str) -> bool:
        """判断是否是当前平台"""
        pass

    @abstractmethod
    async def parse(self, url: str) -> list[str]:
        """返回资源 URL 列表"""
        pass
