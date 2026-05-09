"""
Unit tests for utils/retry.py — validates attempts, delays, and logging.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, call, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.retry import retry_with_backoff


class TestRetryWithBackoff(unittest.TestCase):
    def test_success_on_first_attempt(self):
        """No sleep, no warnings when function succeeds immediately."""
        func = MagicMock(return_value="ok")
        decorated = retry_with_backoff(max_retries=3, base_delay=1)(func)

        with patch("utils.retry.time.sleep") as mock_sleep:
            result = decorated()

        self.assertEqual(result, "ok")
        func.assert_called_once()
        mock_sleep.assert_not_called()

    def test_retries_correct_number_of_times(self):
        """Function is called max_retries times before raising."""
        func = MagicMock(side_effect=ValueError("boom"))
        decorated = retry_with_backoff(max_retries=3, base_delay=1)(func)

        with patch("utils.retry.time.sleep"):
            with self.assertRaises(ValueError):
                decorated()

        self.assertEqual(func.call_count, 3)

    def test_exponential_delays(self):
        """sleep is called with base_delay * 2^attempt for each intermediate failure."""
        func = MagicMock(side_effect=RuntimeError("fail"))
        decorated = retry_with_backoff(max_retries=3, base_delay=2)(func)

        with patch("utils.retry.time.sleep") as mock_sleep:
            with self.assertRaises(RuntimeError):
                decorated()

        # attempts 0 and 1 sleep; attempt 2 (last) raises without sleeping
        self.assertEqual(mock_sleep.call_args_list, [call(2), call(4)])

    def test_no_sleep_on_last_attempt(self):
        """sleep is NOT called after the final failed attempt."""
        func = MagicMock(side_effect=Exception("err"))
        decorated = retry_with_backoff(max_retries=2, base_delay=1)(func)

        with patch("utils.retry.time.sleep") as mock_sleep:
            with self.assertRaises(Exception):
                decorated()

        # only 1 sleep (between attempt 0 and 1); no sleep after attempt 1
        self.assertEqual(mock_sleep.call_count, 1)

    def test_warning_logs_on_intermediate_failures(self):
        """WARNING is logged for each non-final failed attempt."""
        func = MagicMock(side_effect=Exception("err"))
        decorated = retry_with_backoff(max_retries=3, base_delay=1)(func)

        with patch("utils.retry.time.sleep"):
            with self.assertLogs("utils.retry", level="WARNING") as cm:
                with self.assertRaises(Exception):
                    decorated()

        warnings = [r for r in cm.output if "WARNING" in r]
        self.assertEqual(len(warnings), 2)  # attempts 0 and 1

    def test_error_log_on_final_failure(self):
        """ERROR is logged after exhausting all retries."""
        func = MagicMock(side_effect=Exception("final"))
        decorated = retry_with_backoff(max_retries=2, base_delay=1)(func)

        with patch("utils.retry.time.sleep"):
            with self.assertLogs("utils.retry", level="WARNING") as cm:
                with self.assertRaises(Exception):
                    decorated()

        errors = [r for r in cm.output if "ERROR" in r]
        self.assertEqual(len(errors), 1)

    def test_success_after_partial_failures(self):
        """Returns correct value when function succeeds after some failures."""
        func = MagicMock(side_effect=[ValueError("1st"), ValueError("2nd"), "recovered"])
        decorated = retry_with_backoff(max_retries=3, base_delay=1)(func)

        with patch("utils.retry.time.sleep"):
            result = decorated()

        self.assertEqual(result, "recovered")
        self.assertEqual(func.call_count, 3)

    def test_original_exception_type_preserved(self):
        """The exact exception type from the function is re-raised."""
        func = MagicMock(side_effect=KeyError("missing"))
        decorated = retry_with_backoff(max_retries=1, base_delay=1)(func)

        with patch("utils.retry.time.sleep"):
            with self.assertRaises(KeyError):
                decorated()

    def test_wraps_preserves_function_metadata(self):
        """@wraps keeps __name__ and __doc__ of the original function."""

        def my_func():
            """my docstring"""

        decorated = retry_with_backoff()(my_func)
        self.assertEqual(decorated.__name__, "my_func")
        self.assertEqual(decorated.__doc__, "my docstring")


if __name__ == "__main__":
    unittest.main()
