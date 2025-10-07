# main.py
from contextlib import asynccontextmanager
from typing import Optional, Any

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from parser.dy_parse import DyParser
from parser.parser_factory import ParserFactory
from parser.wb_parse import WbParser
from parser.xhs_parse import XhsParser
from util import ip_util

logger.add(
    "logs/log_{time}.log",  # 文件名可以带时间占位
    rotation = "10 MB",  # 文件超过 10 MB 自动切割
    retention = "10 days",  # 只保留 10 天
    compression = "zip",  # 旧文件压缩
    encoding = "utf-8",
    format = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
)


# =========================
# 配置
# =========================
class Settings(BaseSettings):
    APP_NAME: str = "ClipboardDownloadService"
    HOST: str = "0.0.0.0"
    PORT: int = 4999
    DOWNLOAD_DIR: str = "./downloads"
    ALLOWED_ORIGINS: list = ["*"]  # 可根据需要修改
    MAX_FILE_SIZE_MB: int = 200

    class Config:
        env_file = ".env"


settings = Settings()

# 注册解析器
ParserFactory.register(XhsParser())
ParserFactory.register(DyParser())
ParserFactory.register(WbParser())


class ResponseModel(BaseModel):
    code: int = 200
    msg: str = "success"
    platform: str | None = None
    data: Any | None = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

    @classmethod
    def error(cls, msg: str, code: int = 400):
        return cls(code = code, msg = msg, data = None)


# Lifespan 生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    local_ip = ip_util.get_local_ip()
    public_ip = ip_util.get_public_ip()
    logger.info(f"本机局域网 IP: {local_ip}:{settings.PORT}")
    logger.info(f"公网 IP: {public_ip}:{settings.PORT}")
    yield
    # 关闭事件（可选）
    logger.info("服务即将关闭...")


# =========================
# FastAPI 实例
# =========================
app = FastAPI(title = settings.APP_NAME, lifespan = lifespan)
api_router = APIRouter(prefix = "/api/v1")

# =========================
# 中间件
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.ALLOWED_ORIGINS,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)


# 模拟解析函数
async def parse_input_string(input_str: str) -> Optional[str]:
    """
    根据你的项目需求解析输入字符串
    - 如果是 URL，直接返回
    - 如果是文本，需要提取资源 URL
    """
    import re
    if input_str.startswith("http"):
        return input_str

    # 使用正则表达式提取URL
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, input_str)

    if urls:
        return urls[0]  # 返回找到的第一个URL

    return None


# =========================
# 路由
# =========================
class DownloadRequest(BaseModel):
    input_path: str


# @api_router.post("/download", response_model = ResponseModel)
@api_router.post("/download")
async def download_endpoint(req: DownloadRequest):
    """
    接收字符串，解析资源，返回文件下载
    """
    logger.info(f"接收到请求: {req.input_path}")
    url = await parse_input_string(req.input_path)
    if not url:
        return ResponseModel.error("无法解析输入内容")

    parser = await ParserFactory.get_parser(url)
    if not parser:
        return ResponseModel.error("不支持的平台", 500)

    platform = await parser.get_platform()  # ⚠️ 注意加 await
    urls = await parser.parse(url)

    logger.info(f"解析结果: {urls}")
    return ResponseModel(platform = platform.value, data = urls)


app.include_router(api_router)


# =========================
# 健康检查
# =========================
@api_router.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}


# =========================
# 异常处理示例
# =========================
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return ResponseModel.error(exc.detail, exc.status_code)


# =========================
# 启动
# =========================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host = settings.HOST,
        port = settings.PORT,
        reload = True  # 开发模式自动重载
    )

# http://xhslink.com/o/u0vljpIPsM
