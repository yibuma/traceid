import contextvars
import unittest
import unittest.mock
from uuid import uuid4, UUID

from traceid import TraceId, TraceIdNotYetSetError, TraceIdAlreadySetError


class TestTraceId(unittest.TestCase):
    def test_set_get(self):
        # When TraceId is set, it should raise ValueError
        with self.assertRaises(ValueError):
            TraceId.set(None)  # type: ignore
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

    def test_get_exception(self):
        # In unittest, It can't ensure the execution order of test cases.
        # So, it should be restored to the original value.
        old_context_var = TraceId.traceid_var
        TraceId.traceid_var = contextvars.ContextVar("test")
        with self.assertRaises(TraceIdNotYetSetError):
            TraceId.get()

        # Test none value raise TraceIdNotYetSetError too.
        TraceId.traceid_var.set(None)
        with self.assertRaises(TraceIdNotYetSetError):
            TraceId.get()
        TraceId.traceid_var = old_context_var

    def test_clear(self):
        # Ensure TraceId is set
        t_uuid = uuid4()
        TraceId.set(t_uuid, coverage=True)
        self.assertEqual(TraceId.get(), t_uuid)

        # Clear TraceId
        TraceId.clear()
        self.assertFalse(TraceId.is_set())
        with self.assertRaises(TraceIdNotYetSetError):
            TraceId.get()

    def test_is_set(self):
        # When TraceId is not set, it should return False
        TraceId.clear()
        self.assertFalse(TraceId.is_set())
        TraceId.set(uuid4())
        self.assertTrue(TraceId.is_set())

    def test_gen(self):
        # Clear TraceId, ensure TraceId is not set. only in unittest.
        TraceId.clear()

        mock_uuid = UUID("12345678123456781234567812345678")
        with unittest.mock.patch("uuid.uuid4") as mock_uuid4:
            mock_uuid4.return_value = mock_uuid
            TraceId.gen()
        # When TraceId is set, it should return the value
        self.assertIsInstance(TraceId.get(), UUID)
        self.assertEqual(TraceId.get(), mock_uuid)

        # Only first call of gen() should generate a new TraceId
        TraceId.gen()
        self.assertEqual(TraceId.get(), mock_uuid)
