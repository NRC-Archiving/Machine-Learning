import re
from extractors.utils import parse_date

def extract_tenaga_ahli(text):
    """
    Ekstraksi data dari dokumen tenaga ahli.
    """
    patterns = {
        "terbit_date": r"\b[Tt]anggal\s*:\s*(\d{1,2})\s+(\w+)\s+(\d{4})",
        "validity_date": r"sampai\s+dengan\s+tanggal\s*(\d{1,2})\s+(\w+)\s+(\d{4})",
        "nama": r"Nama\s*:\s*(.*)",
        "no_sertifikat": r"No\. Sertifikat\s*:\s*([A-Za-z0-9\-]+)"
    }

    hasil = {}
    try:
        # Ekstraksi tanggal terbit
        terbit_match = re.search(patterns["terbit_date"], text)
        if terbit_match:
            day, month_name, year = terbit_match.groups()
            hasil["terbit_date"] = parse_date(day, month_name, year).strftime("%d-%m-%Y")

        # Ekstraksi tanggal validitas
        validity_match = re.search(patterns["validity_date"], text)
        if validity_match:
            day, month_name, year = validity_match.groups()
            hasil["validity_date"] = parse_date(day, month_name, year).strftime("%d-%m-%Y")

        # Ekstraksi lainnya
        hasil["nama"] = re.search(patterns["nama"], text).group(1) if re.search(patterns["nama"], text) else "N/A"
        hasil["no_sertifikat"] = re.search(patterns["no_sertifikat"], text).group(1) if re.search(patterns["no_sertifikat"], text) else "N/A"
    except Exception as e:
        hasil["error"] = f"Error processing tenaga ahli: {str(e)}"
    return hasil
