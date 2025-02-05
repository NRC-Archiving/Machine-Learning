import re
from extractors.utils import parse_date

def extract_surat_keluar(text):
    patterns = {
        "tanggal": r"\b([A-Z][a-z]*(?: [A-Z][a-z]*)?),\s*(\d{1,2} [A-Z][a-z]+ \d{4})",
        "nomor": r"No(?:mor)?\.?\s*:\s*(.+)",
        "perihal": r"(?i)surat\spernyataan\s*(.*?)\n|(?:Perihal|Hal\.?)\s*:\s*(.+)"
    }

    # Extract values based on patterns
    hasil = {}

    try:
        # Process "tanggal"
        tanggal_match = re.search(patterns["tanggal"], text)
        if tanggal_match:
            _, date_str = tanggal_match.groups()
            try:
                parsed_date = parse_date(date_str)
                hasil["tanggal"] = parsed_date.strftime("%d-%m-%Y")
            except ValueError as e:
                hasil["tanggal"] = f"Error parsing date: {str(e)}"
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
        raise RuntimeError(f"Critical error processing text: {e}")