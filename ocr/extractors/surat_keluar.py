import re
from extractors.utils import parse_date

def extract_surat_keluar(text):
    patterns = {
        "tanggal": r"\b([A-Z][a-z]*(?: [A-Z][a-z]*)?),\s*(\d{1,2} [A-Z][a-z]+ \d{4})",
        "nomor": r"[Nn]o[.:]\s*([^\s]+)",
        "perihal": r"(?i)surat\spernyataan\s*(.*?)\n|[Pp]erihal\s*:\s*([^\s]+)"
    }

    # Extract values based on patterns
    hasil = {}

    try:
        # Process "tanggal"
        tanggal_match = re.search(patterns["tanggal"], text)
        if tanggal_match:
            tanggal_str = tanggal_match.group()
            try:
                tanggal = parse_date(tanggal_str)  # Convert to datetime
                hasil["tanggal"] = tanggal.isoformat()
            except ValueError:
                hasil["tanggal"] = "N/A"
        else:
            hasil["tanggal"] = "N/A"

        # Process "nomor"
        nomor_match = re.search(patterns["nomor"], text)
        hasil["nomor"] = nomor_match.group(1) if nomor_match else "N/A"

        # Process "perihal"
        perihal_match = re.search(patterns["perihal"], text)
        if perihal_match:
            perihal = perihal_match.group(1) or perihal_match.group(2)
            hasil["perihal"] = perihal.strip() if perihal else "N/A"
        else:
            hasil["perihal"] = "N/A"
            
            return hasil

    except Exception as e:
        raise RuntimeError(f"Critical error processing CV: {e}")