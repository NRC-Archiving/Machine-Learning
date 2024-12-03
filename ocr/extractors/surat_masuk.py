import re
from extractors.utils import parse_date

def extract_surat_masuk(text):
    """
    Ekstrak data dari dokumen surat masuk.
    """
    patterns = {
        "tanggal": r"Tanggal\s*:\s*(\d{1,2})\s(\w+)\s(\d{4})",
        "nomor": r"No\.\s*:\s*([^\s]+)",
        "pengirim": r"Hormat\sKami,\s*([^\n]+)",
        "perihal": r"Perihal\s*:\s*(.*)"
    }

    try:
        hasil = {"document_type": "surat_masuk"}

        # Tanggal
        tanggal_match = re.search(patterns["tanggal"], text)
        if tanggal_match:
            day, month_name, year = tanggal_match.groups()
            hasil["tanggal"] = parse_date(day, month_name, year).strftime("%d-%m-%Y")

        # Nomor
        hasil["nomor"] = re.search(patterns["nomor"], text).group(1).strip() if re.search(patterns["nomor"], text) else "N/A"

        # Pengirim
        hasil["pengirim"] = re.search(patterns["pengirim"], text).group(1).strip() if re.search(patterns["pengirim"], text) else "N/A"

        # Perihal
        hasil["perihal"] = re.search(patterns["perihal"], text).group(1).strip() if re.search(patterns["perihal"], text) else "N/A"

        return hasil
    except Exception as e:
        return {"error": f"Error processing surat masuk: {str(e)}"}
