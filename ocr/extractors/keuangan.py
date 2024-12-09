import re
from extractors.utils import parse_date

def extract_keuangan(text):
    """
    Ekstrak data dari dokumen keuangan.
    """
    patterns = {
        "tanggal": (
            r"Printed\s*On\s*:\s*(\d{2}-\w{3}-\d{4})|"
            r"Tanggal\s*Penyampaian\s*:\s*(\d{2}/\d{2}/\d{4})|"
            r"(\w+\s*\d{1,2},\s*\d{4})|"
            r"Tanggal\s*:\s*(\d{2}\s*\w+\s*\d{4})"
        ),
        "periode": (
            r"FROM\s*:\s*(\d{4})|"
            r"Tahun\s*Pajak\s*:\s*(\d{4})|"
            r"yang\s*Berakhir\s*pada\s*.*?(\d{4})|"
            r"sampai\s*dengan\s*tanggal\s*(\d{4})"
        ),
        "nomor": (
            r"(?:Nomor/Number\s?:)\s?([^\s]+)|"
            r"(?:Nomor\s*Tanda\s*Terima\s*Elektronik\s?:)\s?([^\s]+)|"
            r"(?:Nomor\s?:)\s?([^\s]+)"
        ),
    }

    hasil = {}

    try:
        # Extract tanggal
        tanggal_matches = re.findall(patterns["tanggal"], text)
        if tanggal_matches:
            extracted_dates = []
            for match in tanggal_matches:
                for group in match:
                    if group:
                        try:
                            parsed_date = parse_date(group.strip())
                            extracted_dates.append(parsed_date.strftime("%d-%m-%Y"))
                        except ValueError as e:
                            extracted_dates.append(f"Error parsing tanggal: {str(e)}")
                        break
            hasil["tanggal"] = extracted_dates
        else:
            hasil["tanggal"] = ["N/A"]

        # Extract periode (tahun)
        periode_matches = re.findall(patterns["periode"], text)
        if periode_matches:
            extracted_years = []
            for idx, match in enumerate(periode_matches):
                years = [int(year) for year in match if year]
                if idx == 2:  # Case: "yang Berakhir pada ..."
                    if years:
                        extracted_years.append(max(years))  # Take the maximum year
                else:
                    extracted_years.extend(years)
            hasil["tahun"] = list(set(extracted_years))  # Ensure unique years
        else:
            hasil["tahun"] = ["N/A"]

        # Extract nomor
        nomor_matches = re.findall(patterns["nomor"], text)
        if nomor_matches:
            extracted_nomor = [match[0] or match[1] or match[2] for match in nomor_matches]
            hasil["nomor"] = extracted_nomor
        else:
            hasil["nomor"] = ["N/A"]

    except Exception as e:
        hasil["error"] = f"Error processing keuangan: {str(e)}"

    return hasil