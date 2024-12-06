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

    def test_extract_text_output(self):
        """Test text extraction and output the result."""
        # Extract text from the sample PDF
        text = extract_text_from_pdf(self.valid_pdf)

        # Output the extracted text
        print("\nExtracted Text from sample.pdf:")
        print(text)

        # Ensure the extracted text is a string and not empty
        self.assertIsInstance(text, str, "Extracted text should be a string.")
        self.assertGreater(len(text), 0, "Extracted text should not be empty.")

if __name__ == "__main__":
    unittest.main()
