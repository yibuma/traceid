import asyncio
import unittest
from uuid import uuid4, UUID

from traceid import TraceId, TraceIdAlreadySetError


class TestTraceIdAsync(unittest.IsolatedAsyncioTestCase):
    async def test_set_get(self):
        test_uuid1 = uuid4()
        test_uuid2 = uuid4()
        cases = [
            (test_uuid1, test_uuid1),
            (test_uuid2, test_uuid2),
            (12, 12),
            ("test_id1", "test_id1"),
        ]
        for case in cases:
            with self.subTest(case=case):
                TraceId.set(case[0], coverage=True)
                self.assertEqual(TraceId.get(), case[1])

        with self.assertRaises(TraceIdAlreadySetError):
            TraceId.set(test_uuid1)

    async def concurrent_get_method(self, num, sleep: float):
        concurrent_method_name = UUID("1234567812345678123456780000000" + str(num))
        TraceId.set(concurrent_method_name)
        await asyncio.sleep(sleep)
        self.assertEqual(TraceId.get(), concurrent_method_name)

    async def test_multiple_concurrency(self):
        await asyncio.gather(
            self.concurrent_get_method(1, 0.03),
            self.concurrent_get_method(2, 0.02),
            self.concurrent_get_method(3, 0.01),
        )

    async def concurrent_get_method_with_father(self, num, sleep: float):
        concurrent_method_name = UUID("1234567812345678123456780000001" + str(num))
        TraceId.set(concurrent_method_name)
        await asyncio.gather(
            self.concurrent_get_method_with_child(1, concurrent_method_name, 0.03),
            self.concurrent_get_method_with_child(2, concurrent_method_name, 0.02),
            self.concurrent_get_method_with_child(3, concurrent_method_name, 0.01),
        )
        await asyncio.sleep(sleep)
        self.assertEqual(TraceId.get(), concurrent_method_name)

    async def concurrent_get_method_with_child(self, num, old_value, sleep: float):
        self.assertEqual(TraceId.get(), old_value)
        concurrent_method_name = UUID("1234567812345678123456780000002" + str(num))
        TraceId.set(concurrent_method_name, coverage=True)
        await asyncio.sleep(sleep)
        self.assertEqual(TraceId.get(), concurrent_method_name)

    async def test_multiple_concurrency_deep(self):
        await asyncio.gather(
            self.concurrent_get_method_with_father(1, 0.03),
            self.concurrent_get_method_with_father(2, 0.02),
            self.concurrent_get_method_with_father(3, 0.01),
        )
