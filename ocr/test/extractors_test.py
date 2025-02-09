import unittest
import json
import os

from extractors.cv import extract_cv
from preprocessors.pdf_preprocessor import extract_text_from_pdf

class TestExtractorsTruthTable(unittest.TestCase):
    def setUp(self):
        # Define test cases with expected results
        self.test_cases = [
            {
                "pdf_path": "test/test_files/cv_sample.pdf",  # Path to test PDF file (unchanged)
                "expected_output": {
                    "nama": "AGUS MUSLIM, Amd.",
                    "alamat": "Gedung Graha Cipta Lantai 2 JL. D.I Panjaitan No. 40 Jakarta - Timur 13350",
                    "telpon": "(021) - 8193526",
                    "ttl": "Aceh Besar, 17 Agustus 1974",
                    "education": [
                        {
                            "degree": "D3 Teknik Mesin",
                            "institution": "Politeknik Universitas Syiah Kuala",
                            "graduation_year": 1996
                        }
                    ],
                    "latest_experience": {
                        "role": "Supervisor",
                        "project": "Proyek Infrastruktur Subang Smartpolitan",
                        "start_date": "2021-08-01",
                        "end_date": "Present"
                    }
                }
            }
        ]
    
    def test_pdf_to_text_to_extraction(self):
        for case in self.test_cases:
            pdf_text = extract_text_from_pdf(case["pdf_path"])  # Extract text from PDF
            extracted_data = extract_cv(pdf_text)  # Extract structured data from text
            expected_data = case["expected_output"]

            errors = []  # Store assertion failures

            print("\nTruth Table for Test Case:")
            print("Field\tExpected\tExtracted\tMatch")
            print("-" * 80)

            for key in expected_data.keys():
                expected = expected_data[key]
                extracted = extracted_data.get(key, "N/A")
                match = "✔" if expected == extracted else "✘"
                print(f"{key}\t{expected}\t{extracted}\t{match}")

                try:
                    if isinstance(expected, dict):
                        self.assertDictEqual(extracted, expected)
                    elif isinstance(expected, list):
                        self.assertListEqual(extracted, expected)
                    else:
                        self.assertEqual(extracted, expected)
                except AssertionError as e:
                    errors.append(f"Mismatch in {key}: {e}")

            # Display all errors at the end instead of stopping early
            if errors:
                print("\n❌ Test failed with mismatches:")
                for err in errors:
                    print(f"- {err}")
                self.fail("\n".join(errors))

if __name__ == "__main__":
    unittest.main()
