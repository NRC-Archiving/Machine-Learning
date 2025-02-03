import re
from extractors.utils import parse_date

def extract_surat_masuk(text):
    """
    Ekstrak data dari dokumen surat masuk.
    """
    patterns = {
        "tanggal": r"Tanggal\s*:\s*(\d{1,2})\s(\w+)\s(\d{4})|\b([A-Z][a-z]+(?: [A-Z][a-z]+)?),\s*(\d{1,2})\s([A-Z][a-z]+)\s(\d{4})",
        "nomor": r"No[mor]\.\s*:\s*([^\s]+)",
        "pengirim": r"Hormat\sKami,\s*([^\n]+)",
        "perihal": r"Perihal\s*:\s*(.*)"
    }

    try:
        hasil = {"document_type": "surat_masuk"}

        # Extract Tanggal
        tanggal_match = re.search(patterns["tanggal"], text)
        if tanggal_match:
            groups = tanggal_match.groups()
            print("Matched Groups:", groups)  # Debugging line

            day, month_name, year = None, None, None

            # Check if the first pattern (day-month-year) matched
            if groups[0] and groups[1] and groups[2]:  
                day, month_name, year = groups[0], groups[1], groups[2]

            # Check if the second pattern (City, day-month-year) matched
            elif groups[3] and groups[4] and groups[5] and groups[6]:  
                day, month_name, year = groups[4], groups[5], groups[6]  # Correctly extract

            # Ensure extracted values are valid before parsing
            if day and month_name and year:
                date_str = f"{day} {month_name} {year}"  # Combine values into a single string
                hasil["tanggal"] = parse_date(date_str).strftime("%d-%m-%Y")  # Pass correctly)
            else:
                hasil["tanggal"] = "Invalid date format"

        # Extract Nomor
        nomor_match = re.search(patterns["nomor"], text)
        hasil["nomor"] = nomor_match.group(1).strip() if nomor_match else "N/A"

        # Extract Pengirim
        pengirim_match = re.search(patterns["pengirim"], text)
        hasil["pengirim"] = pengirim_match.group(1).strip() if pengirim_match else "N/A"

        # Extract Perihal
        perihal_match = re.search(patterns["perihal"], text)
        hasil["perihal"] = perihal_match.group(1).strip() if perihal_match else "N/A"

        return hasil
    except Exception as e:
        return {"error": f"Error processing surat masuk: {str(e)}"}
