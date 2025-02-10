import re
from extractors.utils import parse_date

def extract_kontrak(text):
    patterns = {
        "tanggal": r"(?:tanggal|hari|tgl,)\s(?:\w+\s)?(\d{1,2})[-\s](\w+)[-\s](\d{4})",
        "nomor_kontrak": r"(?:No\.?\s?:?\s*([^\n]+))|(?:SURAT[^\n]*\n([^\n]+))",
        "nama_proyek": r"(?:PERIHAL\s?:?|Perihal\s?:?|Yang dimaksud dengan Pekerjaan dalam Perjanjian ini adalah)\s?([A-Za-z0-9\-/,(). ]+)",
        "pemberi_kerja": r"(?:Pemberi Tugas\s?:?|PIHAK I\s?:?)\s?(PT\.\s?[A-Za-z0-9., ]+)"
    }

    hasil = {}

    # Tanggal kontrak
    tanggal_match = re.search(patterns["tanggal"], text)
    if tanggal_match:
        day, month_name, year = tanggal_match.groups()
        date_string = f"{day} {month_name} {year}"
        hasil["tanggal"] = parse_date(date_string).strftime("%d-%m-%Y")
    else:
        hasil["tanggal"] = "N/A" 
        

    # Nomor kontrak
    nomor_match = re.search(patterns["nomor_kontrak"], text, re.MULTILINE)
    if nomor_match:
        hasil["nomor_kontrak"] = nomor_match.group(1) or nomor_match.group(2)
    else:
        hasil["nomor_kontrak"] = "N/A"
    # Nama proyek
    hasil["nama_proyek"] = re.search(patterns["nama_proyek"], text).group(1).strip() if re.search(patterns["nama_proyek"], text) else "N/A"

    # Pemberi kerja
    hasil["pemberi_kerja"] = re.search(patterns["pemberi_kerja"], text).group(1).strip() if re.search(patterns["pemberi_kerja"], text) else "N/A"

    return hasil
