import re
from extractors.utils import parse_date

def extract_surat_masuk(text):
    """
    Ekstrak data dari dokumen surat masuk.
    """
    patterns = {
        "tanggal": r"\b([A-Z][a-z]*(?: [A-Z][a-z]*)?),\s*(\d{1,2} [A-Z][a-z]+ \d{4})",
        "nomor": r"Nomor\s*[:;]([^\s]+)|[Nn]o[.:]\s*([^\s]+)",
        "pengirim": r"Hormat Kami,\s*([^\n]+)",
        "perihal": r"Hal\s*:\s*(.*)|Perihal\s*:\s*(.*)"
    }

    try:
        hasil = {}
        # Tanggal
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
        print(hasil["tanggal"])

        # Nomor
        nomor_match = re.search(patterns["nomor"], text)
        hasil["nomor"] = nomor_match.group(1) or nomor_match.group(2) if nomor_match else "N/A"
        print(hasil["nomor"])

        # Pengirim
        pengirim_match = re.search(patterns["pengirim"], text)
        hasil["pengirim"] = pengirim_match.group(1) if pengirim_match else "N/A"
        print(hasil["pengirim"])
        
        # Perihal
        perihal_match = re.search(patterns["perihal"], text)
        hasil["perihal"] = perihal_match.group(1) or perihal_match.group(2) if perihal_match else "N/A"
        print(hasil["perihal"])

        return hasil
    except Exception as e:
        return {"error": f"Error processing surat masuk: {str(e)}"}
