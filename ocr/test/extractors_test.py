import unittest
import json
from extractors.cv import extract_cv  # Import extractor function
from preprocessors.pdf_preprocessor import extract_text_from_pdf  # Import PDF preprocessor
import os

class TestExtractorsTruthTable(unittest.TestCase):
    def setUp(self):
        # Define test cases with expected results
        self.test_cases = [
            {
                "pdf_path": "test_files/dummy_cv.pdf",  # Path to test PDF file
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
            # Step 1: Extract text from PDF
            pdf_text = extract_text_from_pdf(case["pdf_path"])
            
            # Step 2: Extract structured data from text
            extracted_data = extract_cv(pdf_text)
            expected_data = case["expected_output"]
            
            print("\nTruth Table for Test Case:")
            print("Field\tExpected\tExtracted\tMatch")
            print("-" * 50)
            
            for key in expected_data.keys():
                expected = expected_data[key]
                extracted = extracted_data.get(key, "N/A")
                match = "✔" if expected == extracted else "✘"
                print(f"{key}\t{expected}\t{extracted}\t{match}")
                
                if isinstance(expected, dict):
                    self.assertDictEqual(extracted, expected, f"Mismatch in {key}")
                elif isinstance(expected, list):
                    self.assertListEqual(extracted, expected, f"Mismatch in {key}")
                else:
                    self.assertEqual(extracted, expected, f"Mismatch in {key}")

if __name__ == "__main__":
    unittest.main()
