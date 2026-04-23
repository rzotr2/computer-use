import unittest
from unittest.mock import MagicMock, patch
import sys

# Mock pyautogui before importing app.executor
mock_pyautogui = MagicMock()
sys.modules["pyautogui"] = mock_pyautogui

from app.executor import parse_coordinate, process_ollama_response

class TestLogic(unittest.TestCase):
    def test_parse_coordinate(self):
        # Grid size 10, max pixels 1000
        self.assertEqual(parse_coordinate("0", 1000), 0)
        self.assertEqual(parse_coordinate("5", 1000), 500)
        self.assertEqual(parse_coordinate("10", 1000), 1000)

        # Test letters
        self.assertEqual(parse_coordinate("A", 1000), 0)
        self.assertEqual(parse_coordinate("B", 1000), 100)
        self.assertEqual(parse_coordinate("K", 1000), 1000)

    def test_process_ollama_response(self):
        valid_json = '{"thought": "I should click", "action": "CLICK()"}'
        result = process_ollama_response(valid_json)
        self.assertEqual(result["action"], "CLICK()")

        wrapped_json = 'Some text before {"thought": "reason", "action": "MOVE_TO(1, 1)"} some text after'
        result = process_ollama_response(wrapped_json)
        self.assertEqual(result["action"], "MOVE_TO(1, 1)")

if __name__ == "__main__":
    unittest.main()
