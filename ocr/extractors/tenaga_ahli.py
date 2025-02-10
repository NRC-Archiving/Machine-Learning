import re
from dateutil.relativedelta import relativedelta
from extractors.utils import parse_date

def extract_tenaga_ahli(text):
    patterns = {
       "terbit_date": r"(?im)(?:(?:^Tempat\b.*(?:\n|\Z))+)?^(?:Diterbitkan(?: pertama tanggal)?|Diberikan pertama kali pada|tanggal:?|Ditetapkan(?: di \w+)?|(?:[A-Z][a-z]+,))[,:\s]*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})",
        "validity_date": r"sampai(?: dengan tanggal)? (\d{1,2})\s([A-Za-z]+)\s(\d{4})",
        "validity_years": r"berlaku (?:untuk|paling lama) (\d+)",
        "nama": r"([A-Z\s.,\-]+)\nNa?\\?Reg\.",
        "certificate_number": r"No\.\s(?:Reg|Kep)\.\s([\w/.-]+)|Reg\.\s*([A-Za-z0-9\s\-/.]+)(?=\n{1}[^\n])",
        "competency": r"Competency:\s*([^\n]+)"
    }

    hasil = {}
    try:
        # Extract terbit_date
        terbit_match = re.search(patterns["terbit_date"], text)
        if terbit_match:
            day, month_name, year = terbit_match.groups()
            date_str = f"{day} {month_name} {year}"
            try:
                terbit_date = parse_date(date_str)  # Parse the date
                hasil["terbit_date"] = terbit_date.strftime("%d-%m-%Y")
            except Exception as e:
                hasil["terbit_date"] = f"Error parsing terbit_date: {str(e)}"
        else:
            hasil["terbit_date"] = "N/A"

        # Extract validity
        validity_match = re.search(patterns["validity_date"], text)
        if validity_match:
            day, month_name, year = validity_match.groups()
            date_str = f"{day} {month_name} {year}"
            try:
                validity_date = parse_date(date_str)
                hasil["validity"] = validity_date.strftime("%d-%m-%Y")
            except Exception as e:
                hasil["validity"] = f"Error parsing validity_date: {str(e)}"
        else:
            # If no validity_date, check validity_years
            validity_years_match = re.search(patterns["validity_years"], text)
            if validity_years_match and "terbit_date" in hasil and hasil["terbit_date"] != "N/A":
                years = int(validity_years_match.group(1))
                try:
                    validity_date = terbit_date + relativedelta(years=years)
                    hasil["validity"] = validity_date.strftime("%d-%m-%Y")
                except Exception as e:
                    hasil["validity"] = f"Error calculating validity: {str(e)}"
            else:
                hasil["validity"] = "N/A"

        # Extract nama
        nama_match = re.search(patterns["nama"], text)
        hasil["nama"] = nama_match.group(1).strip() if nama_match else "N/A"

        # Extract certificate_number
        certificate_number_match = re.search(patterns["certificate_number"], text, re.MULTILINE)
        if certificate_number_match:
            hasil["certificate_number"] = certificate_number_match.group(1) or certificate_number_match.group(2)
            hasil["certificate_number"] = hasil["certificate_number"].strip() if hasil["certificate_number"] else "N/A"
        else:
            hasil["certificate_number"] = "N/A"

        # Extract competency
        competency_match = re.search(patterns["competency"], text)
        hasil["competency"] = competency_match.group(1).strip() if competency_match else "N/A"

    except Exception as e:
        hasil["error"] = f"Error processing tenaga ahli: {str(e)}"
    
    return hasil
