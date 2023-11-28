import datetime
import json
import logging
import typing
import uuid


from traceid.traceid import TraceId


class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if TraceId.is_set():
            record.trace_id = TraceId.get()
        else:
            record.trace_id = None
        return True


RESERVED: typing.Tuple[str, ...] = (
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "trace_id",
)


class JSONFormatter(logging.Formatter):
    """
    Simple JSON formatter.

    In default configuration, it will output the following fields:
        asctime, levelname, name, module, lineno, trace_id, exc_text, message
    and the following format:
        {"asctime": "2021-01-01T00:00:00.000000+00:00", "levelname": "INFO", "name": "myapp", "module": "myapp", "lineno": 42, "trace_id": "12345678-1234-1234-1234-123456789012", "exc_text": null, "message": "Hello World!"}
    The JSON output can be customized by passing a list of keys to the constructor.
    """

    def __init__(
        self,
        keys: typing.Sequence[str] = [
            "asctime",
            "levelname",
            "name",
            "module",
            "lineno",
            "trace_id",
            "exc_text",
            "message",
        ],
        datetimefmt: str | None = None,
        tzinfo: datetime.tzinfo | None = None,
        json_ensure_ascii: bool = False,
        json_indent: int | None = None,
        json_separators: tuple[str, str] | None = None,
        json_default: typing.Callable[[typing.Any], typing.Any] | None = None,
    ):
        """
        :param keys: List of keys to include in the JSON output.
        :param datetimefmt: Format string for the datetime.strftime() method. defaults to ISO 8601.
        :param tzinfo: Timezone to use for the timestamp. Defaults to local timezone.
        :param json_ensure_ascii: If True, the output is guaranteed to have all incoming non-ASCII characters escaped.
        :param json_indent: If a non-negative integer, then JSON array elements and object members will be pretty-printed
        :param json_separators: If specified, then it should be an (item_separator, key_separator) tuple.
        :param json_default: If specified, then it should be a function that gets called for objects that can’t otherwise be serialized.
        """
        self.keys = keys
        self.datetimefmt = datetimefmt
        self.tzinfo = tzinfo

        self.json_ensure_ascii = json_ensure_ascii
        self.json_indent = json_indent
        self.json_separators = json_separators
        self.json_default = json_default

    def usesTime(self) -> bool:
        return "asctime" in self.keys

    def format_time(self, record: logging.LogRecord) -> str:
        """
        Return the creation time of the specified LogRecord as formatted text.
        """
        if self.tzinfo is None:
            asctime = datetime.datetime.fromtimestamp(record.created).astimezone()
        else:
            asctime = datetime.datetime.fromtimestamp(record.created, self.tzinfo)
        if self.datetimefmt:
            return asctime.strftime(self.datetimefmt)
        else:
            return asctime.isoformat()

    def formatTraceId(self) -> str | None:
        if TraceId.is_set():
            if isinstance(TraceId.get(), uuid.UUID):
                return str(TraceId.get())
            return TraceId.get()  # type: ignore
        else:
            return None

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a record as a JSON string.
        """
        record.trace_id = self.formatTraceId()
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.format_time(record)
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.stack_info:
            record.stack_info = self.formatStack(record.stack_info)

        data = {}
        for key in self.keys:
            if key in RESERVED or hasattr(record, key):
                data[key] = getattr(record, key)
            else:  # pragma: no cover
                raise AttributeError(f"Attribute {key} not found in log record.")

        return json.dumps(
            data,
            ensure_ascii=self.json_ensure_ascii,
            indent=self.json_indent,
            separators=self.json_separators,
            default=self.json_default,
        )
