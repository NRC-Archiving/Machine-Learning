import re
from datetime import datetime, timedelta

# Contoh nilai input
doc_type = 'a'  # Ubah nilai ini sesuai dengan kasus
sub_doc_type = 'x'  # Nilai default jika tidak diberikan
text = "sampai dengan tanggal 12 Januari 2025, berlaku paling lama 3 tahun"
tanggal_terbit = datetime.strptime("2023-01-01", "%Y-%m-%d")  # Contoh tanggal terbit, bisa diganti


# Mapping nama bulan ke nomor bulan
month_mapping = {
    "Januari"|"Jan"|"January": "01", "Februari"|"Feb"|"February": "02", "Maret"|"Mar"|"March": "03", "April"|"Apr": "04",
    "Mei"|"May": "05", "Juni"|"Jun"|"June": "06", "Juli"|"Jul"|"July": "07", "Agustus"|"Agu"|"Aug"|"Augustus": "08",
    "September"|"Sep": "09", "Oktober"|"Okt"|"Oct"|"October": "10", "November"|"Nov": "11", "Desember"|"Des"|"Dec"|"December": "12"
}

# Inisialisasi dictionary output
masa_berlaku = {}

# Menggunakan match-case untuk menentukan regex pattern berdasarkan doc_type dan sub_doc_type
match (doc_type, sub_doc_type):
    case ('legalitas', _):
        
        # Regex pattern untuk doc_type 'a'
        date_pattern = re.compile(r"sampai(?: dengan tanggal)? (\d{1,2})\s([A-Za-z]+)\s(\d{4})")
        years_pattern = re.compile(r"berlaku (?:untuk|paling lama) (\d+)")
        
        # Ekstrak informasi tanggal dan masa berlaku sesuai dengan snippet sebelumnya
        for match in date_pattern.finditer(text):
            day, month_name, year = match.groups()
            month_number = month_mapping.get(month_name, "00")
            formatted_date = f"{day.zfill(2)}-{month_number}-{year}"
            masa_berlaku[f"case_{match.start()}"] = formatted_date

        # Ekstrak informasi tahun untuk menghitung tanggal kedaluwarsa
        for match in years_pattern.finditer(text):
            years = int(match.group(1))
            expiration_date = tanggal_terbit + timedelta(days=365 * years)
            masa_berlaku[f"case_{match.start()}"] = expiration_date.strftime("%d-%m-%Y")

    case ('b', _):
        # Placeholder untuk kasus 'b'
        masa_berlaku["case_b"] = "Logika untuk doc_type b"

    case ('c', _):
        # Placeholder untuk kasus 'c'
        masa_berlaku["case_c"] = "Logika untuk doc_type c"

    case ('d', _):
        # Placeholder untuk kasus 'd'
        masa_berlaku["case_d"] = "Logika untuk doc_type d"

    case ('e', _):
        # Placeholder untuk kasus 'e'
        masa_berlaku["case_e"] = "Logika untuk doc_type e"

    case ('f', _):
        # Placeholder untuk kasus 'f'
        masa_berlaku["case_f"] = "Logika untuk doc_type f"

    case ('g', _):
        # Placeholder untuk kasus 'g'
        masa_berlaku["case_g"] = "Logika untuk doc_type g"

    case ('h', _):
        # Placeholder untuk kasus 'h'
        masa_berlaku["case_h"] = "Logika untuk doc_type h"

    case ('i', _):
        # Placeholder untuk kasus 'i'
        masa_berlaku["case_i"] = "Logika untuk doc_type i"

    case ('j', _):
        # Placeholder untuk kasus 'j'
        masa_berlaku["case_j"] = "Logika untuk doc_type j"

    case _:
        print("Doc_type atau sub_doc_type tidak dikenali, tidak ada pola yang cocok.")

print(masa_berlaku)
