import re
from extractors.utils import parse_date

def extract_kontrak(text):
    patterns = {
        "tanggal": r"(?:tanggal|hari)\s(?:\w+\s)?(\d{1,2})[-\s](\w+)[-\s](\d{4})",
        "nomor_kontrak": r"(?:No\.?\s?:?|SURAT\s)([A-Za-z0-9/\-]+)",
        "nama_proyek": r"(?:PERIHAL\s?:?|Perihal\s?:?|Yang dimaksud dengan Pekerjaan dalam Perjanjian ini adalah)\s?([A-Za-z0-9\-/,(). ]+)",
        "pemberi_kerja": r"(?:Pemberi Tugas\s?:?|PIHAK I\s?:?)\s?(PT\.\s?[A-Za-z0-9., ]+)"
    }

    hasil = {}

    # Tanggal kontrak
    tanggal_match = re.search(patterns["tanggal"], text)
    if tanggal_match:
        day, month_name, year = tanggal_match.groups()
        hasil["tanggal"] = parse_date(day, month_name, year).strftime("%d-%m-%Y")

    # Nomor kontrak
    hasil["nomor_kontrak"] = re.search(patterns["nomor_kontrak"], text).group(1).strip() if re.search(patterns["nomor_kontrak"], text) else "N/A"

    # Nama proyek
    hasil["nama_proyek"] = re.search(patterns["nama_proyek"], text).group(1).strip() if re.search(patterns["nama_proyek"], text) else "N/A"

    # Pemberi kerja
    hasil["pemberi_kerja"] = re.search(patterns["pemberi_kerja"], text).group(1).strip() if re.search(patterns["pemberi_kerja"], text) else "N/A"

    return hasil
