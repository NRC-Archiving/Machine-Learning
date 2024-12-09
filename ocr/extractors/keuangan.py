import re
from extractors.utils import parse_date

def extract_keuangan(text):
    """
    Ekstrak data dari dokumen keuangan.
    """
    patterns = {
        "tanggal": r"Printed\s*On\s*:\s*(\d{2}-\w{3}-\d{4})|Tanggal\s*Penyampaian\s*:\s*(\d{2}/\d{2}/\d{4})|(\w+\s*\d{1,2},\s*\d{4})|Tanggal\s*:\s*(\d{2}\s*\w+\s*\d{4})",
        "periode": r"FROM\s*:\s*(\d{4})|Tahun\s*Pajak\s*:\s*(\d{4})|yang\s*Berakhir\s*pada\s*.*?(\d{4})|sampai\s*dengan\s*tanggal\s*(\d{4})",
        "nomor": r"(?<=Nomor/Number\s?:)\s?([^\s]+)|(?<=Nomor\s*Tanda\s*Terima\s*Elektronik\s?:)\s?([^\s]+)|(?<=Nomor\s?:)\s?([^\s]+)"
    }

    try:
        
        hasil = {}
        # Tanggal
        tanggal_match = re.search(patterns["tanggal"], text)
        if tanggal_match:
            hasil["tanggal"] = tanggal_match.group(1).strip() if tanggal_match else "N/A"

        # Tahun pajak
        hasil["tahun"] = re.search(patterns["tahun"], text).group(1) if re.search(patterns["tahun"], text) else "N/A"

        # Nomor
        hasil["nomor"] = re.search(patterns["nomor"], text).group(1).strip() if re.search(patterns["nomor"], text) else "N/A"

        return hasil
    except Exception as e:
        return {"error": f"Error processing keuangan: {str(e)}"}
