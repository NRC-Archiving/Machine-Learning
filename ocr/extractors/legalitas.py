import re
from extractors.utils import parse_date

def extract_legalitas(text):
    """
    Ekstraksi data dari dokumen legalitas.
    """
    patterns = {
        "tanggal_terbit": r"\b[Tt]anggal\s*:\s*(\d{1,2})\s+(\w+)\s+(\d{4})",
        "masa_berlaku": r"sampai\s+dengan\s+tanggal\s*(\d{1,2})\s+(\w+)\s+(\d{4})",
        "penerbit": r"(?<=diterbitkan oleh\s*:\s*)([A-Z][^:]+)",
        "nomor_dokumen": r"Nomor\s*:\s*([A-Za-z0-9\-]+)"
    }

    hasil = {}
    try:
        # Ekstraksi tanggal terbit
        terbit_match = re.search(patterns["tanggal_terbit"], text)
        if terbit_match:
            day, month_name, year = terbit_match.groups()
            hasil["tanggal_terbit"] = parse_date(day, month_name, year).strftime("%d-%m-%Y")

        # Ekstraksi masa berlaku
        masa_match = re.search(patterns["masa_berlaku"], text)
        if masa_match:
            day, month_name, year = masa_match.groups()
            hasil["masa_berlaku"] = parse_date(day, month_name, year).strftime("%d-%m-%Y")

        # Ekstraksi lainnya
        hasil["penerbit"] = re.search(patterns["penerbit"], text).group(1) if re.search(patterns["penerbit"], text) else "N/A"
        hasil["nomor_dokumen"] = re.search(patterns["nomor_dokumen"], text).group(1) if re.search(patterns["nomor_dokumen"], text) else "N/A"
    except Exception as e:
        hasil["error"] = f"Error processing legalitas: {str(e)}"
    return hasil
