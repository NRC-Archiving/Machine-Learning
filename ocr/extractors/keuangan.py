import re
from extractors.utils import parse_date

def extract_keuangan(text):
    """
    Ekstrak data dari dokumen keuangan.
    """
    patterns = {
        "tanggal": r"Printed\sOn\s*:\s*(\d{2}-\w{3}-\d{4})|Tanggal\s*Penyampaian\s*:\s*(\d{2}/\d{2}/\d{4})",
        "tahun_pajak": r"Tahun\sPajak\s*:\s*(\d{4})",
        "nomor": r"Nomor\s*:\s*([^\s]+)"
    }

    try:
        hasil = {"document_type": "keuangan"}

        # Tanggal
        tanggal_match = re.search(patterns["tanggal"], text)
        if tanggal_match:
            hasil["tanggal"] = tanggal_match.group(1).strip() if tanggal_match else "N/A"

        # Tahun pajak
        hasil["tahun_pajak"] = re.search(patterns["tahun_pajak"], text).group(1) if re.search(patterns["tahun_pajak"], text) else "N/A"

        # Nomor
        hasil["nomor"] = re.search(patterns["nomor"], text).group(1).strip() if re.search(patterns["nomor"], text) else "N/A"

        return hasil
    except Exception as e:
        return {"error": f"Error processing keuangan: {str(e)}"}
