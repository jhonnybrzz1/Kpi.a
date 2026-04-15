"""
Unit tests for validation utilities
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.validation import validate_input, sanitize_text, validate_api_response


class TestValidateInput(unittest.TestCase):
    """Test cases for validate_input function"""

    def test_valid_input(self):
        """Test that valid input passes validation"""
        result = validate_input("This is a valid initiative description")
        self.assertTrue(result["valid"])

    def test_empty_input(self):
        """Test that empty input fails validation"""
        result = validate_input("")
        self.assertFalse(result["valid"])
        self.assertIn("descrição", result["message"])

    def test_whitespace_only(self):
        """Test that whitespace only fails validation"""
        result = validate_input("   \n\t  ")
        self.assertFalse(result["valid"])

    def test_minimum_length(self):
        """Test that input below minimum length fails"""
        result = validate_input("Short")
        self.assertFalse(result["valid"])
        self.assertIn("10 caracteres", result["message"])

    def test_maximum_length(self):
        """Test that input above maximum length fails"""
        long_text = "A" * 5001
        result = validate_input(long_text)
        self.assertFalse(result["valid"])
        self.assertIn("5000 caracteres", result["message"])

    def test_no_valid_characters(self):
        """Test that input without valid characters fails"""
        result = validate_input("1234567890 !@#$%")
        self.assertFalse(result["valid"])

    def test_valid_with_special_chars(self):
        """Test that valid input with special characters passes"""
        result = validate_input("Initiative: café & negócio válido!")
        self.assertTrue(result["valid"])


class TestSanitizeText(unittest.TestCase):
    """Test cases for sanitize_text function"""

    def test_basic_sanitization(self):
        """Test basic text sanitization"""
        result = sanitize_text("  Hello   World  ")
        self.assertEqual(result, "Hello World")

    def test_remove_html_tags(self):
        """Test that HTML tags are removed"""
        result = sanitize_text("<script>alert('xss')</script>Safe text")
        self.assertNotIn("<script>", result)
        self.assertIn("Safe text", result)

    def test_remove_control_characters(self):
        """Test that control characters are removed"""
        # Control character \x00
        result = sanitize_text("Text\x00 with control")
        self.assertNotIn("\x00", result)

    def test_empty_string(self):
        """Test empty string handling"""
        result = sanitize_text("")
        self.assertEqual(result, "")

    def test_none_input(self):
        """Test None input handling"""
        result = sanitize_text(None)
        self.assertEqual(result, "")

    def test_unicode_characters(self):
        """Test that unicode characters are preserved"""
        result = sanitize_text("Café résumé naïve")
        self.assertEqual(result, "Café résumé naïve")


class TestValidateApiResponse(unittest.TestCase):
    """Test cases for validate_api_response function"""

    def test_valid_response(self):
        """Test valid response with all required fields"""
        response = {"field1": "value1", "field2": "value2"}
        result = validate_api_response(response, ["field1", "field2"])
        self.assertTrue(result)

    def test_missing_field(self):
        """Test response with missing required field"""
        response = {"field1": "value1"}
        result = validate_api_response(response, ["field1", "field2"])
        self.assertFalse(result)

    def test_non_dict_response(self):
        """Test that non-dict response fails"""
        result = validate_api_response(["item1", "item2"], ["field1"])
        self.assertFalse(result)

    def test_empty_response(self):
        """Test empty dict response"""
        result = validate_api_response({}, ["field1"])
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
