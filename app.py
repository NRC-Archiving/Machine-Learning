#Impoorting necessary library
from pdf2image import convert_from_path
import pytesseract
import cv2
from PIL import Image
import os
import argparse
import re
import json
import re
from datetime import datetime, timedelta


# Preprocessing
def process_image(image_path, preprocess_method):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if preprocess_method == "trunc":
        gray = cv2.threshold(gray, 127, 255, cv2.THRESH_trunc)[1]

    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)

    text = pytesseract.image_to_string(Image.open(filename))
    print(f"Text from {image_path}:\n{text}\n")

    cv2_imshow(image)
    cv2_imshow(gray)
    cv2.waitKey(0)
    return text, filename  # Return the extracted text and temporary filename

all_text = ""
temporary_files = []  # List to store temporary filenames

# Loop through image files
i = 1
while True:
    image_path = f"page_image_{i}.jpg"
    if os.path.exists(image_path):
        text, temp_file = process_image(image_path, args["preprocess"])
        all_text += text
        temporary_files.append(temp_file)  # Add temporary filename to list
        i += 1
    else:
        break

with open("all_text.txt", "w") as f:
    f.write(all_text)
print("All images processed.")

# Delete temporary files after processing all images
for temp_file in temporary_files:
    os.remove(temp_file)
print("Temporary files deleted.")


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
        # Placeholder untuk kasus 'c'
        masa_berlaku["case_c"] = "Logika untuk doc_type c"
    
    case ('tenaga_ahli', _):
        
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

    case ('kontrak', _):
        # Placeholder untuk kasus 'b'
        masa_berlaku["case_b"] = "Logika untuk doc_type b"

    case ('cv', _):
        # Placeholder untuk kasus 'd'
        masa_berlaku["case_d"] = "Logika untuk doc_type d"

    case ('keuangan', _):
        # Placeholder untuk kasus 'e'
        masa_berlaku["case_e"] = "Logika untuk doc_type e"

    case ('proyek', _):
        # Placeholder untuk kasus 'f'
        masa_berlaku["case_f"] = "Logika untuk doc_type f"

    case ('pengurus'|"pemegang_saham", _):
        # Placeholder untuk kasus 'g'
        masa_berlaku["case_g"] = "Logika untuk doc_type g"

    case ('peralatan', _):
        # Placeholder untuk kasus 'h'
        masa_berlaku["case_h"] = "Logika untuk doc_type h"

    case ('lain_lain', _):
        # Placeholder untuk kasus 'i'
        masa_berlaku["case_i"] = "Logika untuk doc_type i"

    case ('surat_masuk', _):
        # Placeholder untuk kasus 'j'
        masa_berlaku["case_j"] = "Logika untuk doc_type j"

    case ('surat_keluar', _):
        # Placeholder untuk kasus 'j'
        masa_berlaku["case_j"] = "Logika untuk doc_type j"

    case ('sertifikat', _):
        # Placeholder untuk kasus 'j'
        masa_berlaku["case_j"] = "Logika untuk doc_type j"

    case ('ppjb', _):
        # Placeholder untuk kasus 'j'
        masa_berlaku["case_j"] = "Logika untuk doc_type j"    

    case _:
        print("Doc_type atau sub_doc_type tidak dikenali, tidak ada pola yang cocok.")

print(masa_berlaku)
