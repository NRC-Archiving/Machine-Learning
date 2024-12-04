import os
import unittest
from app import app

class TestAppIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up the test client and test data."""
        cls.client = app.test_client()  # Flask test client
        cls.test_files_dir = "test/test_files/"  # Directory for test PDFs
        cls.test_cases = [
            {
                "file": "cv_sample.pdf",
                "doc_type": "cv",
                "expected_keys": ["nama", "education", "experiences", "total_years_of_experience"]
            },
            {
                "file": "keuangan_sample.pdf",
                "doc_type": "keuangan",
                "expected_keys": ["tanggal", "tahun_pajak", "nomor"]
            },
            {
                "file": "legalitas_sample.pdf",
                "doc_type": "legalitas",
                "expected_keys": ["tanggal_terbit", "masa_berlaku", "penerbit", "nomor_dokumen"]
            }
        ]

    def test_integration(self):
        for case in self.test_cases:
            file_path = os.path.join(self.test_files_dir, case["file"])
            with open(file_path, "rb") as test_file:
                response = self.client.post(
                    "/extract",
                    data={"file": test_file, "doc_type": case["doc_type"]},
                    content_type="multipart/form-data"
                )
                self.assertEqual(response.status_code, 200)

                # Parse JSON response
                response_data = response.get_json()
                self.assertIsNotNone(response_data)

                # Verify expected keys in the result
                for key in case["expected_keys"]:
                    self.assertIn(key, response_data)

    def test_invalid_file(self):
        invalid_file_path = os.path.join(self.test_files_dir, "invalid_file.txt")
        with open(invalid_file_path, "rb") as invalid_file:
            response = self.client.post(
                "/extract",
                data={"file": invalid_file, "doc_type": "cv"},
                content_type="multipart/form-data"
            )
            self.assertEqual(response.status_code, 400)
            response_data = response.get_json()
            self.assertIn("error", response_data)

    def test_missing_file(self):
        response = self.client.post(
            "/extract",
            data={"doc_type": "cv"},
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        response_data = response.get_json()
        self.assertIn("error", response_data)

if __name__ == "__main__":
    unittest.main()
