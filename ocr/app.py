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
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)


# Direktori penyimpanan file yang diunggah
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/your-endpoint', methods=['GET', 'POST'])
def your_endpoint():
    # Get parameters from request
    doc_type = request.args.get('doc_type', 'a')  # default to 'a' if not provided
    sub_doc_type = request.args.get('sub_doc_type', 'x')  # default to 'x' if not provided

# Cek apakah ada file dalam request
    if 'file' not in request.files:
        return jsonify({"error": "Tidak ada file yang diunggah"}), 400
    
    file = request.files['file']

    # Validasi apakah file memiliki nama dan format yang benar
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "File harus dalam format PDF"}), 400
    
    # Simpan file secara aman
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        file.save(file_path)
    except Exception as e:
        app.logger.error(f"Error saving file: {e}")
        return jsonify({"error": "Failed to save file"}), 500

    # Do something with doc_type and sub_doc_type
    result = {
        "doc_type": doc_type,
        "sub_doc_type": sub_doc_type
    }
    
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


    # Mapping nama bulan ke nomor bulan
    month_mapping = {
        "Januari"|"Jan"|"January": "01", "Februari"|"Feb"|"February": "02", "Maret"|"Mar"|"March": "03", "April"|"Apr": "04",
        "Mei"|"May": "05", "Juni"|"Jun"|"June": "06", "Juli"|"Jul"|"July": "07", "Agustus"|"Agu"|"Aug"|"Augustus": "08",
        "September"|"Sep": "09", "Oktober"|"Okt"|"Oct"|"October": "10", "November"|"Nov": "11", "Desember"|"Des"|"Dec"|"December": "12"
    }
    # Function to parse date strings with month name mapping
    def parse_date(day, month_name, year):
        month_number = month_mapping.get(month_name, "00")
        return datetime.strptime(f"{day.zfill(2)}-{month_number}-{year}", "%d-%m-%Y")

    # Menggunakan match-case untuk menentukan regex pattern berdasarkan doc_type dan sub_doc_type
    match (doc_type, sub_doc_type):

        case ('legalitas', _):
            # Pattern Legalitas
            patterns = {
                "terbit_date":r"(?:di\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*tanggal:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4}))|(?:[Dd]iterbitkan pertama tanggal|[Dd]iberikan pertama kali pada|[Tt]anggal:|[Dd]itetapkan di \w+,?)\s*(\d{1,2})\s(\w+)\s(\d{4})",
                "validity_date": r"sampai(?: dengan tanggal)? (\d{1,2})\s([A-Za-z]+)\s(\d{4})",
                "validity_years": r"berlaku (?:untuk|paling lama) (\d+)",
                "penerbit": r"(?:\b[a-z]+(?:\s+[a-z]+)+\b\s+)([A-Z][^:]+)(?=\s*menetapkan\s+bahwa)|(?<=ditetapkan\s+oleh\s*:\s*)([A-Z][^:]+)|(?<=diterbitkan\s+sistem\s+)(\S+)(?=\s+berdasarkan)|(?<=^|\n)([A-Z][^:]+)(?=\s*menetapkan\s+bahwa)",
                "doc_number": r"No\. Reg\.\s([A-Za-z0-9\s]+)(?=\n)|(?<=Nomor:\s*)(\d+)|(?<=Nomor:\n)(\d+)|(?<=Certificate No\.\s)([A-Za-z0-9\.\s]+?)(?=\n|$)|(?<=NOMOR INDUK BERUSAHA\s*:\s*)([A-Za-z0-9]+)(?=\n|$)",
            }
            
            # Extracting information using patterns
            masa_berlaku = {}
            tanggal_terbit = None

            # Extract tanggal terbit
            terbit_match = re.search(patterns["terbit_date"], text)
            if terbit_match:
                day, month_name, year = terbit_match.groups()
                tanggal_terbit = parse_date(day, month_name, year)
                masa_berlaku["tanggal_terbit"] = tanggal_terbit.strftime("%d-%m-%Y")

            # Extract validity dates
            for match in re.finditer(patterns["validity_date"], text):
                day, month_name, year = match.groups()
                formatted_date = parse_date(day, month_name, year).strftime("%d-%m-%Y")
                masa_berlaku[f"case_{match.start()}"] = formatted_date

            # Extract validity years and calculate expiration dates
            for match in re.finditer(patterns["validity_years"], text):
                years = int(match.group(1))
                expiration_date = tanggal_terbit + timedelta(days=365 * years)
                masa_berlaku[f"case_{match.start()}"] = expiration_date.strftime("%d-%m-%Y")
            
            # Extract 'penerbit'
            penerbit_match = re.search(patterns["penerbit"], text)
            penerbit = penerbit_match.group(0).strip() if penerbit_match else "N/A"

            # Extract 'doc_number'
            doc_number_match = re.search(patterns["doc_number"], text)
            doc_number = doc_number_match.group(0).strip() if doc_number_match else "N/A"

            # Custom output for 'legalitas' document type
            output = {
                "document_type": "legalitas",
                "penerbit": penerbit,
                "masa_berlaku": masa_berlaku.get("tanggal_terbit"),
                "doc_number":doc_number
            }
            return jsonify(output)
        
        case ('tenaga_ahli', _):
            
            # Pattern Tenaga Ahli
            patterns = {
                "terbit_date": r"\b(?:[Dd]iterbitkan pertama tanggal|[Dd]iberikan pertama kali pada|[Tt]anggal:|[Dd]itetapkan di \w+,?)\s*(\d{1,2})\s(\w+)\s(\d{4})",
                "validity_date": r"sampai(?: dengan tanggal)? (\d{1,2})\s([A-Za-z]+)\s(\d{4})",
                "validity_years": r"berlaku (?:untuk|paling lama) (\d+)",
                "nama": r"(?<=This is to certify that,\n)(.*)",
                "certificate_number": r"No\. Reg\.\s([A-Za-z0-9\s]+)(?=\n)",
                "competency": r"(?<=Competency:\n)(.*)"
            }

            # Extracting information using patterns
            masa_berlaku = {}
            tanggal_terbit = None

            # Extract tanggal terbit
            terbit_match = re.search(patterns["terbit_date"], text)
            if terbit_match:
                day, month_name, year = terbit_match.groups()
                tanggal_terbit = parse_date(day, month_name, year)
                masa_berlaku["tanggal_terbit"] = tanggal_terbit.strftime("%d-%m-%Y")

            # Extract validity dates
            for match in re.finditer(patterns["validity_date"], text):
                day, month_name, year = match.groups()
                formatted_date = parse_date(day, month_name, year).strftime("%d-%m-%Y")
                masa_berlaku[f"case_{match.start()}"] = formatted_date

            # Extract validity years and calculate expiration dates
            for match in re.finditer(patterns["validity_years"], text):
                years = int(match.group(1))
                expiration_date = tanggal_terbit + timedelta(days=365 * years)
                masa_berlaku[f"case_{match.start()}"] = expiration_date.strftime("%d-%m-%Y")

            # Extract additional fields
            nama = re.search(patterns["nama"], text).group(1).strip() if re.search(patterns["nama"], text) else None
            cert_number = re.search(patterns["certificate_number"], text).group(1).strip() if re.search(patterns["certificate_number"], text) else None
            competency = re.search(patterns["competency"], text).group(1).strip() if re.search(patterns["competency"], text) else None

            # Prepare output
            output = {
                "document_type": "tenaga_ahli",
                "tanggal_terbit": masa_berlaku.get("tanggal_terbit"),
                "validity_period": masa_berlaku,
                "nama": nama,
                "certificate_number": cert_number,
                "competency": competency
            }
            return jsonify(output)

        case ('kontrak', _):
            # Placeholder untuk kasus 'b'
            masa_berlaku["case_b"] = "Logika untuk doc_type b"

            output = {
                "document_type": "kontrak",
                "status": "processed",
                "contract_details": "Details specific to contract documents",
                "masa_berlaku": masa_berlaku,
            }
            return jsonify(output)

        case ('cv', _):
            # Pattern CV
            patterns = {
                "experience": r"(\b\w+\s\d{4}\s-\s(?:\w+\s\d{4}|Present))\s*:\s*(.*)\n([\s\S]+?)(?=\n\n|\Z)",
                "nama": r"Nama\s*:\s*(.*)",
                "ttl": r"Tempat & Tgl\. Lahir\s*:\s*(.*)",
                "education": r"Pendidikan\s*:\s*(.*?)\s(.*?)\s*-\s*(\d{4})"
            }

            # Function to parse date strings
            def parse_date(date_str):
                return datetime.strptime(date_str, "%B %Y") if date_str != "Present" else datetime.now()

            # Extract personal details
            nama = re.search(patterns["nama"], text).group(1)
            ttl = re.search(patterns["ttl"], text).group(1)
            education = re.search(patterns["education"], text)
            univ, gelar, lulus = education.groups()

            # Parse experience entries
            experiences = []
            for date_range, role, project in re.findall(patterns["experience"], text):
                company_name = re.search(r"(.*)\n" + re.escape(date_range), text).group(1).strip()
                start_date, end_date = map(parse_date, date_range.split(" - "))
                duration = (end_date - start_date).days / 365.25

                experiences.append({
                    "company": company_name,
                    "role": role or "No role specified",
                    "project": project.replace("\n", " "),
                    "start_date": start_date,
                    "end_date": end_date,
                    "duration_years": duration
                })

            # Determine the latest project experience and total years of experience
            latest_experience = max(experiences, key=lambda x: x["end_date"])
            total_years = round(sum(exp["duration_years"] for exp in experiences), 2)

            # Prepare output as JSON with only latest project experience and total years of experience
            output = {
                    "latest_project": latest_experience["project"],
                    "total_years_of_experience": total_years,
                    "nama": nama,
                    "ttl": ttl,
                    "gelar": gelar,
                    "univ": univ,
                    "lulus": lulus
                }

            return jsonify(output)


        case ('keuangan', _):
            # Pattern Keuangan
            masa_berlaku["case_e"] = "Logika untuk doc_type e"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('proyek', _):
            # Pattern Proyek
            masa_berlaku["case_f"] = "Logika untuk doc_type f"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('pengurus'|"pemegang_saham", _):
            # Pattern Pengurus dan Pemegang saham
            masa_berlaku["case_g"] = "Logika untuk doc_type g"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('peralatan', _):
            # Pattern Peralatan
            masa_berlaku["case_h"] = "Logika untuk doc_type h"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('lain_lain', _):
            # Pattern Dokumen Lain-lain
            masa_berlaku["case_i"] = "Logika untuk doc_type i"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('surat_masuk', _):
            # Patern Surat Masuk
            masa_berlaku["case_j"] = "Logika untuk doc_type j"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('surat_keluar', _):
            # Pattern Surat Keluar
            masa_berlaku["case_j"] = "Logika untuk doc_type j"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('sertifikat', _):
            # Pattern Sertifikat Tanah
            masa_berlaku["case_j"] = "Logika untuk doc_type j"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('ppjb', _):
            # Pattern PPJB
            masa_berlaku["case_j"] = "Logika untuk doc_type j"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)    

        # Case diluar jenis dokumen yanga ada
        case _:
            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)


if __name__ == '__main__':
    app.run(debug=True)