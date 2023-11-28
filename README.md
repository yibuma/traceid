# TraceId
[![codecov](https://codecov.io/gh/yibuma/traceid/graph/badge.svg?token=D0xBb4lMqA)](https://codecov.io/gh/yibuma/traceid)  

TraceId is a trace ID generator based on [Python contextvars](https://docs.python.org/3/library/contextvars.html). It automatically passes the trace ID in asynchronous tasks, enabling cross-coroutine tracing.

## Installation

### Install via pip
```
pip install traceid
```

### Install via poetry

```
poetry add traceid
```

## Usage

### Generate trace ID
```python
from traceid import TraceId
TraceId.gen()
```

### Set trace ID
```python
from traceid import TraceId
TraceId.set('your trace id')
```

### Get trace ID
```python
from traceid import TraceId
TraceId.get()
```

### Clear trace ID
```python
from traceid import TraceId
TraceId.clear()
```

### Check if trace ID has been set/generated
```python
from traceid import TraceId
TraceId.is_set()
```

### Integrate with Fastapi
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

### Integrate with logging
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