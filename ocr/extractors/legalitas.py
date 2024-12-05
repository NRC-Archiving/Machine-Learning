import re
from extractors.utils import parse_date

def extract_legalitas(text):
    """
    Ekstraksi data dari dokumen legalitas.
    """
    patterns = {
        "tanggal_terbit": r"\b[Tt]anggal\s*:\s*(\d{1,2})\s+(\w+)\s+(\d{4})",
        "masa_berlaku": r"(?:sampai\s+dengan\s+tanggal\s*(\d{1,2})\s+(\w+)\s+(\d{4}))|(?:Masa\s+Berlaku\s+s\.d\.\s*:\s*(\d{4}-\d{2}-\d{2}))",
        "penerbit": r"(?<=diterbitkan oleh\s*:\s*)([A-Z][^:]+)",
        "nomor_dokumen": r"Nomor\s*:\s*([A-Za-z0-9\-]+)"
    }

    hasil = {}
    try:
        # Ekstraksi tanggal terbit
        terbit_match = re.search(patterns["tanggal_terbit"], text)
        if terbit_match:
            day, month_name, year = terbit_match.groups()
            date_str = f"{day} {month_name} {year}"
            hasil["tanggal_terbit"] = parse_date(date_str).strftime("%d-%m-%Y")
        else:
            hasil["tanggal_terbit"] = "N/A"

        # Ekstraksi masa berlaku
        masa_match = re.search(patterns["masa_berlaku"], text)
        if masa_match:
            if masa_match.group(1):  # Original format
                day, month_name, year = masa_match.groups()[:3]
                date_str = f"{day} {month_name} {year}"
                hasil["masa_berlaku"] = parse_date(date_str).strftime("%d-%m-%Y")
            elif masa_match.group(4):  # New format
                hasil["masa_berlaku"] = masa_match.group(4)
        else:
            hasil["masa_berlaku"] = "N/A"

        # Ekstraksi lainnya
        penerbit_match = re.search(patterns["penerbit"], text)
        hasil["penerbit"] = (
            penerbit_match.group(1) if penerbit_match else "N/A"
        )

        nomor_dokumen_match = re.search(patterns["nomor_dokumen"], text)
        hasil["nomor_dokumen"] = (
            nomor_dokumen_match.group(1) if nomor_dokumen_match else "N/A"
        )
    except Exception as e:
        hasil["error"] = f"Error processing legalitas: {str(e)}"
    return hasil
