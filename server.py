import datetime
from sanic import Sanic, json, response
from sanic.worker.manager import WorkerManager
from functools import partial
import os
import yaml
from app.utils import fetch_and_transform_config
from app.config import config_manager

# Sanic app configuration
app = Sanic("ClashProxy")
app.config.REQUEST_TIMEOUT = 300
app.config.REQUEST_MAX_SIZE = 1000000000

# Clash proxy configurations
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "") # 支持逗号隔开，比如 aaa,bbb

@app.get("/")
async def welcome(_):
    return json({
        "success": True,
        "message": "欢迎使用 Clash 配置转换服务",
    })

@app.get("/link/<token>")
async def get_subscription(_, token: str):
    """Get transformed Clash configuration"""
    # 支持多个 token，用逗号分隔
    valid_tokens = [t.strip() for t in AUTH_TOKEN.split(",")]
    if token not in valid_tokens:
        return json({
            "code": 403,
            "message": "无效的访问令牌",
            "data": None
        }, status=403)
    
    config = config_manager.load_config()
    if not config["url"]:
        return json({
            "code": 400,
            "message": "未配置订阅地址",
            "data": None
        }, status=400)
    
    try:
        # 尝试首先从缓存加载
        cached_config = config_manager.load_cached_proxy()
        if cached_config and not config_manager.need_update():
            # 如果有缓存且不需要更新,直接返回缓存的配置
            return response.text(
                yaml.dump(cached_config, allow_unicode=True),
                content_type="text/plain; charset=utf-8"
            )
        
        # 如果没有缓存，则获取并转换
        transformed_config = fetch_and_transform_config(config["url"])
        config_manager.save_cached_proxy(transformed_config)
        config_manager.update_last_update_time()
        return response.text(
            yaml.dump(transformed_config, allow_unicode=True),
            content_type="text/plain; charset=utf-8"
        )
    except Exception as e:
        return json({
            "code": 500,
            "message": str(e),
            "data": None
        }, status=500)

if __name__ == '__main__':
    cpu_count = int(os.getenv('WORKER_COUNT', '1'))
    print(f"Starting server with {cpu_count} workers")
    app.run(host='0.0.0.0', port=8000, workers=cpu_count)