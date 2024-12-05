import unittest
import os
from preprocessors.pdf_preprocessor import extract_text_from_pdf

class TestPDFPreprocessor(unittest.TestCase):
    """Unit tests for the PDF preprocessor."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_files_dir = "test/test_files/"
        cls.valid_pdf = os.path.join(cls.test_files_dir, "sample.pdf")
        cls.invalid_pdf = os.path.join(cls.test_files_dir, "invalid.pdf")
        cls.non_pdf_file = os.path.join(cls.test_files_dir, "invalid_file.txt")

    def test_extract_text_valid_pdf(self):
        """Test text extraction from a valid PDF."""
        text = extract_text_from_pdf(self.valid_pdf)
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0, "Extracted text should not be empty.")
        self.assertIn("Sample", text, "Extracted text should contain expected content.")

    def test_extract_text_invalid_pdf(self):
        """Test handling of an invalid or corrupted PDF."""
        with self.assertRaises(Exception) as context:
            extract_text_from_pdf(self.invalid_pdf)
        self.assertIn("Error", str(context.exception), "Error message should indicate failure.")

    def test_extract_text_non_pdf_file(self):
        """Test handling of a non-PDF file."""
        with self.assertRaises(Exception) as context:
            extract_text_from_pdf(self.non_pdf_file)
        self.assertIn("Error", str(context.exception), "Error message should indicate invalid file type.")

    def test_extract_text_missing_file(self):
        """Test handling of a missing file."""
        with self.assertRaises(FileNotFoundError):
            extract_text_from_pdf("non_existent_file.pdf")

if __name__ == "__main__":
    unittest.main()
