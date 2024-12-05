import re
from extractors.utils import parse_date

def extract_tenaga_ahli(text):
    patterns = {
        "terbit_date": r"\b(?:Diterbitkan pertama tanggal|Diberikan pertama kali pada|tanggal:|Ditetapkan di \w+,?)\s*(\d{1,2})\s(\w+)\s(\d{4})",
        "validity_date": r"sampai(?: dengan tanggal)? (\d{1,2})\s([A-Za-z]+)\s(\d{4})",
        "validity_years": r"berlaku (?:untuk|paling lama) (\d+)",
        "nama": r"(?<=This is to certify that,\n)(.*)",
        "certificate_number": r"No\. Reg\.\s([A-Za-z0-9\s]+)(?=\n)",
        "competency": r"(?<=Competency:\n)(.*)"
    }

    hasil = {}
    try:
        # Extract terbit_date
        terbit_match = re.search(patterns["terbit_date"], text)
        if terbit_match:
            day, month_name, year = terbit_match.groups()
            date_str = f"{day} {month_name} {year}"
            terbit_date = parse_date(date_str)  # Save the parsed terbit_date
            hasil["terbit_date"] = terbit_date.strftime("%d-%m-%Y")
        else:
            terbit_date = None
            hasil["terbit_date"] = "N/A"

        # Extract validity
        validity_match = re.search(patterns["validity_date"], text)
        if validity_match:
            day, month_name, year = validity_match.groups()
            date_str = f"{day} {month_name} {year}"
            validity_date = parse_date(date_str)
            hasil["validity"] = validity_date.strftime("%d-%m-%Y")
        else:
            # If no validity_date, check validity_years
            validity_years_match = re.search(patterns["validity_years"], text)
            if validity_years_match and terbit_date:
                years = int(validity_years_match.group(1))
                validity_date = terbit_date.replace(year=terbit_date.year + years)
                hasil["validity"] = validity_date.strftime("%d-%m-%Y")
            else:
                hasil["validity"] = "N/A"

        # Extract nama
        nama_match = re.search(patterns["nama"], text)
        hasil["nama"] = nama_match.group(1).strip() if nama_match else "N/A"

        # Extract certificate_number
        certificate_number_match = re.search(patterns["certificate_number"], text)
        hasil["certificate_number"] = certificate_number_match.group(1).strip() if certificate_number_match else "N/A"

        # Extract competency
        competency_match = re.search(patterns["competency"], text)
        hasil["competency"] = competency_match.group(1).strip() if competency_match else "N/A"

    except Exception as e:
        hasil["error"] = f"Error processing tenaga ahli: {str(e)}"
    
    return hasil
