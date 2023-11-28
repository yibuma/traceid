# TraceId
[![codecov](https://codecov.io/gh/yibuma/traceid/graph/badge.svg?token=D0xBb4lMqA)](https://codecov.io/gh/yibuma/traceid)  

TraceId 是一个基于 [Python contextvars](https://docs.python.org/3/library/contextvars.html) 实现的跟踪 ID 生成器，它可以在异步任务中自动传递跟踪 ID，从而实现跨协程的跟踪。

## 安装

### 通过 pip 安装
```
pip install traceid
```

### 通过 poetry 安装
```
poetry add traceid
```

## 使用

### 生成跟踪 ID
```python
from traceid import TraceId
TraceId.gen()
```

### 设置跟踪 ID
```python
from traceid import TraceId
TraceId.set('your trace id')
```

### 获取跟踪 ID
```python
from traceid import TraceId
TraceId.get()
```

### 清除跟踪 ID
```python
from traceid import TraceId
TraceId.clear()
```

### 检查是否已经设置/生成跟踪 ID
```python
from traceid import TraceId
TraceId.is_set()
```

### 与 Fastapi 集成
```python
import typing

from fastapi import FastAPI, Request, Response
from traceid import TraceId
from aiorow import Connection, DSN


app = FastAPI()

@app.middleware("http")
async def add_trace_id(
    request: Request, call_next: typing.Callable[[Request], typing.Awaitable[Response]]
) -> Response:
    trace_id = request.headers.get("X-Request-ID", None)
    if trace_id is None:
        TraceId.gen()
    else:
        TraceId.set(trace_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(TraceId.get())
    return response
@app.get("/")
def read_root():
    return {"Hello": "World"}
```
### 日志中使用跟踪 ID
```python
import logging
import logging.config
import os

from traceid import JSONFormatter


LOG_SETTINGS = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": logging.INFO,
            "formatter": "json",
        },
    },
    "formatters": {
        "json": {
            "()": JSONFormatter,
        },
    },
    "loggers": {
        "": {"level": logging.INFO, "handlers": ["console"], "propagate": True},
    },
}

logging.config.dictConfig(LOG_SETTINGS)
```