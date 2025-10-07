from parser.base_parse import BaseParser


class ParserFactory:
    _parsers: list[BaseParser] = []

    @classmethod
    def register(cls, parser: BaseParser):
        cls._parsers.append(parser)

    @classmethod
    async def get_parser(cls, input_str: str) -> BaseParser:
        for parser in cls._parsers:
            if await parser.is_me(input_str):
                return parser
        return None
