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

    # Inisialisasi dictionary output
    masa_berlaku = {}

    # Menggunakan match-case untuk menentukan regex pattern berdasarkan doc_type dan sub_doc_type
    match (doc_type, sub_doc_type):

        case ('legalitas', _):
            # Placeholder untuk kasus 'c'
            masa_berlaku["case_c"] = "Logika untuk doc_type c"


            # Custom output for 'legalitas' document type
            output = {
                "document_type": "legalitas",
                "status": "processed",
                "additional_info": "Legal document information extracted successfully",
                "masa_berlaku": masa_berlaku,
                # Add any additional relevant fields here
            }
            return jsonify(output)
        
        case ('tenaga_ahli', _):
            
            # Regex pattern untuk doc_type 'a'
            terbit_pattern = re.compile(r"\b(?:diterbitkan pertama tanggal|diberikan pertama kali pada|tanggal:|ditetapkan di \w+,?)\s*(\d{1,2})\s(\w+)\s(\d{4})")
            date_pattern = re.compile(r"sampai(?: dengan tanggal)? (\d{1,2})\s([A-Za-z]+)\s(\d{4})")
            years_pattern = re.compile(r"berlaku (?:untuk|paling lama) (\d+)")
            
            masa_berlaku = {}
            tanggal_terbit = None

            # Determine tanggal_terbit from terbit_pattern
            terbit_match = terbit_pattern.search(text)
            if terbit_match:
                day, month_name, year = terbit_match.groups()
                month_number = month_mapping.get(month_name, "00")
                tanggal_terbit = datetime.strptime(f"{day.zfill(2)}-{month_number}-{year}", "%d-%m-%Y")
                masa_berlaku["tanggal_terbit"] = tanggal_terbit.strftime("%d-%m-%Y")

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

            output = {
                "document_type": "tenaga_ahli",
                "status": "processed",
                "tanggal_terbit": masa_berlaku.get("tanggal_terbit"),
                "validity_period": masa_berlaku,
                "additional_info": "Expert document processed with extracted validity dates",
                # Additional fields as needed
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
            # Placeholder untuk kasus 'd'
            pattern = r"(\b\w+\s\d{4}\s-\s(?:\w+\s\d{4}|Present))\s*:\s*(.*)\n([\s\S]+?)(?=\n\n|\Z)"
            nama_pattern = r"nama|Nama\s*:\s*(.*)"

            nama_match = re.search(nama_pattern, text)
            nama = nama_match.group(1) if nama_match else None

            # Parse entries into a list of dictionaries
            matches = re.findall(pattern, text)
            experiences = []

            # Function to convert date strings to datetime objects
            def parse_date(date_str):
                try:
                    return datetime.strptime(date_str, "%B %Y")
                except ValueError:
                    return None  # If the date is "Present", return None

            # Loop through matches and parse dates
            for match in matches:
                date_range, role, project_details = match

                # Extract company name from the previous line in text
                # by matching company name preceding the date range line
                company = re.search(r"(.*)\n" + re.escape(date_range), text)
                company_name = company.group(1).strip() if company else "Unknown Company"

                start_date_str, end_date_str = date_range.split(" - ")

                # Convert start and end dates to datetime objects
                start_date = parse_date(start_date_str)
                end_date = parse_date(end_date_str) if end_date_str != "Present" else datetime.now()

                # Calculate experience duration in years
                duration = (end_date - start_date).days / 365.25

                experiences.append({
                    "company": company_name,
                    "role": role if role else "No role specified",
                    "project": project_details.strip().replace("\n", " "),
                    "start_date": start_date,
                    "end_date": end_date,
                    "duration_years": duration,
                    "nama": nama
                })

            # Determine the latest experience with a project
            if any(exp["end_date"] == datetime.now() for exp in experiences):
                # Case with "Present": Filter and choose the first experience with "Present"
                latest_experience = next(exp for exp in experiences if exp["end_date"] == datetime.now())
            else:
                # Case with only past date ranges: Sort by end date to find the latest
                latest_experience = sorted(experiences, key=lambda x: x["end_date"], reverse=True)[0]

            # Calculate the total years of experience
            total_years = sum(exp["duration_years"] for exp in experiences)

            # Prepare output as JSON with only latest project experience and total years of experience
            output = {
                "latest_project": latest_experience["project"],
                "total_years_of_experience": round(total_years, 2),
                "nama": nama

            }

            return jsonify(output)



        case ('keuangan', _):
            # Placeholder untuk kasus 'e'
            masa_berlaku["case_e"] = "Logika untuk doc_type e"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('proyek', _):
            # Placeholder untuk kasus 'f'
            masa_berlaku["case_f"] = "Logika untuk doc_type f"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('pengurus'|"pemegang_saham", _):
            # Placeholder untuk kasus 'g'
            masa_berlaku["case_g"] = "Logika untuk doc_type g"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('peralatan', _):
            # Placeholder untuk kasus 'h'
            masa_berlaku["case_h"] = "Logika untuk doc_type h"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('lain_lain', _):
            # Placeholder untuk kasus 'i'
            masa_berlaku["case_i"] = "Logika untuk doc_type i"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('surat_masuk', _):
            # Placeholder untuk kasus 'j'
            masa_berlaku["case_j"] = "Logika untuk doc_type j"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('surat_keluar', _):
            # Placeholder untuk kasus 'j'
            masa_berlaku["case_j"] = "Logika untuk doc_type j"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('sertifikat', _):
            # Placeholder untuk kasus 'j'
            masa_berlaku["case_j"] = "Logika untuk doc_type j"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)

        case ('ppjb', _):
            # Placeholder untuk kasus 'j'
            masa_berlaku["case_j"] = "Logika untuk doc_type j"

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "doc_type": doc_type,
                "sub_doc_type": sub_doc_type
            }
            return jsonify(output)    

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