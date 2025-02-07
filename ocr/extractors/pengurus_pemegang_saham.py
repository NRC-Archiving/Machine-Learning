import re

def extract_pengurus_pemegang_saham(text="text", doc_type="pengurus"):
    patterns = {
        "nama": r"NPWP\s*:\s*\d{2}\.\d{3}\.\d{3}\.\d-\d{3}\.\d{3}\s*\n(.+)",
        "npwp": r"NPWP\s*:\s*(\d{2}\.\d{3}\.\d{3}\.\d-\d{3}\.\d{3})",
        "nik": r"NIK\s*[:|;|=]\s*(\d{16})",
        "alamat": r"NIK\s*[:|;|=]\s*\d{16}\s*-?\s*\n(.*?)(?=\n\n|$)"
    }

    try:
        hasil = {}
        
        # Ekstraksi nama
        nama_match = re.search(patterns["nama"], text)
        hasil["nama"] = nama_match.group(1).strip() if nama_match else "N/A"

        # Ekstraksi NPWP
        npwp_match = re.search(patterns["npwp"], text)
        hasil["npwp"] = npwp_match.group(1).strip() if npwp_match else "N/A"

        # Ekstraksi NIK hanya jika jenis dokumen berupa pengurus
        if doc_type == "pengurus":
            nik_match = re.search(patterns["nik"], text)
            hasil["nik"] = nik_match.group(1).strip() if nik_match else "N/A"

        # Extract Address (All lines after NIK)
        alamat_match = re.search(patterns["alamat"], text, re.DOTALL)
        if alamat_match:
            alamat_lines = alamat_match.group(1).strip().split("\n")
            hasil["alamat"] = ", ".join([line.strip() for line in alamat_lines if line.strip()])
        else:
            hasil["alamat"] = "N/A"

        return hasil
    except Exception as e:
        return {"error": f"Error processing pengurus or pemegang saham: {str(e)}"}
