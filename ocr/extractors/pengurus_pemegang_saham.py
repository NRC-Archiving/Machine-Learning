import re

def extract_pengurus_pemegang_saham(text):
    patterns = {
        "nama": r"NPWP\s*:\s*\d{2}\.\d{3}\.\d{3}\.\d-\d{3}\.\d{3}\s*\n(.+)",
        "npwp": r"NPWP\s*:\s*(\d{2}\.\d{3}\.\d{3}\.\d-\d{3}\.\d{3})",
        "nik": r"NIK\s*[:|;|=]\s*(\d{16})",
        "kota": r"(?i)PROVINSI.*\n(.*)",
        "alamat": r"Alamat\s*:\s*(.*?)(?=\n\n|$)"
    }

    try:
        hasil = {}
        
        # Ekstraksi nama
        nama_match = re.search(patterns["nama"], text)
        hasil["nama"] = nama_match.group(1).strip() if nama_match else "N/A"

        # Ekstraksi NPWP
        npwp_match = re.search(patterns["npwp"], text)
        hasil["npwp"] = npwp_match.group(1).strip() if npwp_match else "N/A"

        # Ekstraksi NIK
        nik_match = re.search(patterns["nik"], text)
        hasil["nik"] = nik_match.group(1).strip() if nik_match else "N/A"

        # Ekstraksi alamat
        alamat_match = re.search(patterns["alamat"], text, re.DOTALL)
        if alamat_match:
            alamat_lines = alamat_match.group(1).split("\n")
            alamat = ", ".join([line.strip() for line in alamat_lines if line.strip()])
        else:
            alamat = "N/A"

        # Ekstraksi kota (internal only)
        kota_match = re.search(patterns["kota"], text)
        kota = kota_match.group(1).strip() if kota_match else "N/A"

        # Combine kota into alamat directly
        if alamat != "N/A" and kota != "N/A":
            alamat = f"{alamat}, {kota}"

        # Save the final alamat into the result
        hasil["alamat"] = alamat

        return hasil
    except Exception as e:
        return {"error": f"Error processing pengurus or pemegang saham: {str(e)}"}
