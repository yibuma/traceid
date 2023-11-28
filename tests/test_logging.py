import datetime
import logging
import inspect
import io
import json
import uuid
import unittest
import unittest.mock
import zoneinfo

from traceid.logging import JSONFormatter, TraceIdFilter
from traceid.traceid import TraceId


class TestLogging(unittest.TestCase):
    def test_filter(self):
        TraceId.clear()
        with unittest.mock.patch("sys.stdout", new=io.StringIO()) as fake_out:
            ch = logging.StreamHandler(stream=fake_out)
            ch.setFormatter(logging.Formatter("%(trace_id)s-%(levelname)s-%(message)s"))
            ch.addFilter(TraceIdFilter())

            logger = logging.getLogger("test")
            logger.setLevel(logging.INFO)
            logger.addHandler(ch)

            logger.info("test without trace id")

            self.assertEqual(fake_out.getvalue(), "None-INFO-test without trace id\n")

            fake_out.truncate(0)
            fake_out.seek(0)

            t_uuid = uuid.uuid4()
            TraceId.set(t_uuid)
            logger.info("test with trace id")
            self.assertEqual(fake_out.getvalue(), f"{t_uuid}-INFO-test with trace id\n")

    def test_formatter_normal(self):
        TraceId.clear()
        with unittest.mock.patch("sys.stdout", new=io.StringIO()) as fake_out:
            ch = logging.StreamHandler(stream=fake_out)
            ch.setFormatter(JSONFormatter(keys=["trace_id", "levelname", "message"]))

            logger = logging.getLogger("test")
            logger.setLevel(logging.INFO)
            logger.addHandler(ch)

            # test without trace id
            logger.info("test without trace id")
            self.assertEqual(
                json.loads(fake_out.getvalue()),
                {
                    "trace_id": None,
                    "levelname": "INFO",
                    "message": "test without trace id",
                },
            )

            fake_out.truncate(0)
            fake_out.seek(0)
            # test with trace id
            t_uuid = uuid.uuid4()
            TraceId.set(t_uuid)
            logger.info("test with trace id")
            self.assertEqual(
                json.loads(fake_out.getvalue()),
                {
                    "trace_id": str(t_uuid),
                    "levelname": "INFO",
                    "message": "test with trace id",
                },
            )
            fake_out.truncate(0)
            fake_out.seek(0)
            # test with string trace id
            t_id = "test_id"
            TraceId.set(t_id, coverage=True)
            logger.info("test with test_id")
            self.assertEqual(
                json.loads(fake_out.getvalue()),
                {
                    "trace_id": t_id,
                    "levelname": "INFO",
                    "message": "test with test_id",
                },
            )

    def test_formatter_with_timezone(self):
        TraceId.clear()
        now = 1234567890
        with unittest.mock.patch(
            "sys.stdout", new=io.StringIO()
        ) as fake_out, unittest.mock.patch("time.time", new=lambda: now):
            ch = logging.StreamHandler(stream=fake_out)

            logger = logging.getLogger("test")
            logger.setLevel(logging.INFO)
            logger.addHandler(ch)

            t_uuid = uuid.uuid4()
            TraceId.set(t_uuid)

            # test with asctime
            ch.setFormatter(
                JSONFormatter(keys=["asctime", "trace_id", "levelname", "message"])
            )
            logger.info("test with asctime")
            self.assertEqual(
                json.loads(fake_out.getvalue()),
                {
                    "asctime": datetime.datetime.fromtimestamp(now)
                    .astimezone()
                    .isoformat(),
                    "trace_id": str(t_uuid),
                    "levelname": "INFO",
                    "message": "test with asctime",
                },
            )

            fake_out.truncate(0)
            fake_out.seek(0)
            # test with tzinfo
            ch.setFormatter(
                JSONFormatter(
                    keys=["asctime", "trace_id", "levelname", "message"],
                    tzinfo=zoneinfo.ZoneInfo("America/New_York"),
                )
            )
            logger.info("test with tzinfo")
            self.assertEqual(
                json.loads(fake_out.getvalue()),
                {
                    "asctime": datetime.datetime.fromtimestamp(
                        now, zoneinfo.ZoneInfo("America/New_York")
                    ).isoformat(),
                    "trace_id": str(t_uuid),
                    "levelname": "INFO",
                    "message": "test with tzinfo",
                },
            )

            fake_out.truncate(0)
            fake_out.seek(0)
            # test with datetimefmt
            ch.setFormatter(
                JSONFormatter(
                    keys=["asctime", "trace_id", "levelname", "message"],
                    datetimefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            logger.info("test with datetimefmt")
            self.assertEqual(
                json.loads(fake_out.getvalue()),
                {
                    "asctime": datetime.datetime.fromtimestamp(now)
                    .astimezone()
                    .strftime("%Y-%m-%d %H:%M:%S"),
                    "trace_id": str(t_uuid),
                    "levelname": "INFO",
                    "message": "test with datetimefmt",
                },
            )

    def test_formatter_with_exc_text(self):
        TraceId.clear()
        with unittest.mock.patch("sys.stdout", new=io.StringIO()) as fake_out:
            ch = logging.StreamHandler(stream=fake_out)

            logger = logging.getLogger("test")
            logger.setLevel(logging.INFO)
            logger.addHandler(ch)

            t_uuid = uuid.uuid4()
            TraceId.set(t_uuid)

            # test with exc_text = None
            ch.setFormatter(
                JSONFormatter(
                    keys=["trace_id", "levelname", "message", "exc_text", "stack_info"]
                )
            )
            logger.info("test with asctime")
            self.assertEqual(
                json.loads(fake_out.getvalue()),
                {
                    "trace_id": str(t_uuid),
                    "levelname": "INFO",
                    "message": "test with asctime",
                    "exc_text": None,
                    "stack_info": None,
                },
            )

            fake_out.truncate(0)
            fake_out.seek(0)
            logger.warning(
                "test with exc_text", exc_info=RuntimeError("test"), stack_info=True
            )
            log = json.loads(fake_out.getvalue())
            self.assertTrue(isinstance(log["stack_info"], str))
            self.assertTrue(
                log["stack_info"].startswith("Stack (most recent call last):")
            )
            lineno = inspect.currentframe().f_lineno - 8  # type: ignore
            self.assertTrue(
                f'{__file__}", line {lineno},' in log["stack_info"],
                msg=log["stack_info"],
            )
            self.assertEqual(
                log,
                {
                    "trace_id": str(t_uuid),
                    "levelname": "WARNING",
                    "message": "test with exc_text",
                    "exc_text": "RuntimeError: test",
                    "stack_info": log["stack_info"],
                },
            )
