import re
from datetime import datetime
from extractors.utils import parse_date

def extract_keuangan(text):
    """
    Ekstrak data dari dokumen keuangan.
    """
    patterns = {
        "tanggal": r"Printed\s*On\s*:\s*(\d{2}-\w{3}-\d{4})|Tanggal\s*Pen[vy]ampaian\s*:\s*(\d{2}/\d{2}/\d{4})|/\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})|Tanggal\s*:\s*(\d{2}\s*\w+\s*\d{4})",
        "periode": r"FROM\s*:\s*(\d{4})|Tahun\s*Pajak\s*:\s*(\d{4})|yang\s*Berakhir\s*pada\s*.*?(\d{4})|sampai\s*dengan\s*tanggal\s*(\d{4})",
        "nomor": r"(?:Subsidiary\s+No\.?\s?)([\dA-Za-z/-]+)|(?:Nomor/Number\s?:)\s?([^\s]+)|(?:Nomor\sTanda\sTerima\sElektronik\s?:)\s?([\d/-]+)|(?:Nomor\s?:)\s?([^\s]+)"
    }

    hasil = {}

    try:
        # Extract 'tanggal' (dates)
        tanggal_matches = re.search(patterns["tanggal"], text)
        if tanggal_matches:
            raw_tanggal = next((match for match in tanggal_matches.groups() if match), None)
            if raw_tanggal:
                preprocessed_tanggal = raw_tanggal.replace("-", " ")
                try:
                    hasil["tanggal"] = parse_date(preprocessed_tanggal).strftime("%d-%m-%Y")
                except ValueError:
                    # Fallback logic for invalid date format
                    try:
                        fallback_date = datetime.strptime(preprocessed_tanggal, "%d/%m/%Y")
                        hasil["tanggal"] = fallback_date.strftime("%d-%m-%Y")
                    except ValueError:
                        hasil["tanggal"] = f"Invalid date: {preprocessed_tanggal}"
            else:
                hasil["tanggal"] = "N/A"
        else:
            hasil["tanggal"] = "N/A"

        # Extract 'periode' (tahun)
        periode_matches = re.search(patterns["periode"], text)
        if periode_matches:
            hasil["tahun"] = next((year for year in periode_matches.groups() if year), "N/A")
        else:
            hasil["tahun"] = "N/A"

        # Extract 'nomor'
        nomor_matches = re.search(patterns["nomor"], text)
        if nomor_matches:
            hasil["nomor"] = next((match for match in nomor_matches.groups() if match), "N/A")
        else:
            hasil["nomor"] = "N/A"

    except Exception as e:
        hasil["error"] = f"Error processing keuangan: {str(e)}"

    return hasil