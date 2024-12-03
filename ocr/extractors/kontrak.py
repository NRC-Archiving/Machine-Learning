import re
from extractors.utils import parse_date

def extract_kontrak(text):
    """
    Ekstrak data dari dokumen kontrak.
    """
    patterns = {
        "tanggal": r"Tanggal\s*:\s*(\d{1,2})\s(\w+)\s(\d{4})",
        "nomor_kontrak": r"No\.\sKontrak\s*:\s*([A-Za-z0-9\-]+)",
        "nama_proyek": r"Nama\sProyek\s*:\s*(.*)",
        "pemberi_kerja": r"Pemberi\sKerja\s*:\s*(.*)"
    }

    try:
        hasil = {"document_type": "kontrak"}

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
    except Exception as e:
        return {"error": f"Error processing kontrak: {str(e)}"}
