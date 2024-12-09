import unittest
import os
import asyncio
from preprocessors.pdf_preprocessor import extract_text_from_pdf_async

class TestPDFPreprocessor(unittest.TestCase):
    """Unit tests for the PDF preprocessor."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.test_files_dir = "test/test_files/"
        cls.valid_pdf = os.path.join(cls.test_files_dir, "sample_keuangan.pdf")

    def test_extract_text_output(self):
        """Test text extraction and output the result."""
        # Run the asynchronous function synchronously using asyncio.run
        text = asyncio.run(extract_text_from_pdf_async(self.valid_pdf, doc_type="keuangan"))

        # Output the extracted text
        print("\nExtracted Text from sample_keuangan.pdf:")
        print(text)

        # Ensure the extracted text is a string and not empty
        self.assertIsInstance(text, str, "Extracted text should be a string.")
        self.assertGreater(len(text), 0, "Extracted text should not be empty.")

if __name__ == "__main__":
    unittest.main()
