import re
from extractors.utils import parse_date

def extract_cv(text):
    """
    Extract data from CV document with enhanced error handling.
    """
    patterns = {
        "nama": r"Nama\s*:\s*(.*)",
        "alamat": r"Alamat Kantor\s*:\s*(.*?)\nTelpon",
        "telpon": r"Te[le]pon\s*:\s*(.*?)(?=\n|$)",
        "ttl": r"Lahir\s*:\s*(.*?)(?=\n|$)",
        "education": r"Pendidikan\s*:\s*(.*?)\n(?:\s*(.*?)\s-\s(\d{4}))*",
        "degree_year": r"(\D+)\s-\s(\d{4})",
        "experience": r"(\w+\s\d{4})\s*-\s*(Sekarang|Present)\s*([^\n]+)\n([^\n]*)"    
        }

    try:
        results = {}

        # Extract name
        nama_match = re.search(patterns["nama"], text)
        results["nama"] = nama_match.group(1).strip() if nama_match else "N/A"

        # Extract address
        alamat_match = re.search(patterns["alamat"], text, re.DOTALL)
        if alamat_match:
            alamat_raw = alamat_match.group(1).strip()
            results["alamat"] = re.sub(r"\s*\n\s*", " ", alamat_raw)  # Replace newlines with spaces
        else:
            results["alamat"] = "N/A"

        # Extract phone numbers
        telpon_match = re.search(patterns["telpon"], text)
        results["telpon"] = telpon_match.group(1).strip().replace("\n", ", ") if telpon_match else "N/A"

        # Extract place and date of birth
        ttl_match = re.search(patterns["ttl"], text)
        results["ttl"] = ttl_match.group(1).strip() if ttl_match else "N/A"

        # Extract education details
        education_match = re.search(patterns["education"], text, re.DOTALL)
        if education_match:
            institution = education_match.group(1).strip()
            degree_year_matches = re.findall(r"(.+?)\s-\s(\d{4})", education_match.group(0))
            results["education"] = [
                {"institution": institution, "degree": degree.strip(), "graduation_year": int(year)}
                for degree, year in degree_year_matches
            ]
        else:
            results["education"] = []

        # Extract the entry with "Sekarang" or "Present"
        match = re.search(patterns["experience"], text, re.DOTALL)
        if match:
            start_date_str, end_date_str, role, project_line = match.groups()
            try:
                # Parse start date
                start_date = parse_date(start_date_str).strftime("%Y-%m-%d")

                # Assign "Present" as the end date
                end_date = "Present"

                # Construct the latest experience result
                latest_experience = {
                    "start_date": start_date,
                    "end_date": end_date,
                    "role": role.strip(),
                    "project": project_line.strip() if project_line else "N/A"
                }
            except Exception as exp_err:
                raise RuntimeError(f"Error parsing experience entry: {exp_err}")
        else:
            latest_experience = None  # No match found
            
        # Assign the result
        results["latest_experience"] = latest_experience

        return results

    except Exception as e:
        raise RuntimeError(f"Critical error processing CV: {e}")
