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
    month_names = [
    ["Januari", "Jan", "January"],
    ["Februari", "Feb", "February"],
    ["Maret", "Mar", "March"],
    ["April", "Apr"],
    ["Mei", "May"],
    ["Juni", "Jun", "June"],
    ["Juli", "Jul", "July"],
    ["Agustus", "Agu", "Aug", "August"],
    ["September", "Sep"],
    ["Oktober", "Okt", "Oct", "October"],
    ["November", "Nov"],
    ["Desember", "Des", "Dec", "December"]
    ]

    month_mapping = {}
    for i, names in enumerate(month_names):
        for name in names:
            month_mapping[name] = f"{i + 1:02}"

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
            terbit_match = re.search(patterns["terbit_date"], all_text)
            if terbit_match:
                day, month_name, year = terbit_match.groups()
                tanggal_terbit = parse_date(day, month_name, year)
                masa_berlaku["tanggal_terbit"] = tanggal_terbit.strftime("%d-%m-%Y")

            # Extract validity dates
            for match in re.finditer(patterns["validity_date"], all_text):
                day, month_name, year = match.groups()
                formatted_date = parse_date(day, month_name, year).strftime("%d-%m-%Y")
                masa_berlaku[f"case_{match.start()}"] = formatted_date

            # Extract validity years and calculate expiration dates
            for match in re.finditer(patterns["validity_years"], all_text):
                years = int(match.group(1))
                expiration_date = tanggal_terbit + timedelta(days=365 * years)
                masa_berlaku[f"case_{match.start()}"] = expiration_date.strftime("%d-%m-%Y")
            
            # Extract 'penerbit'
            penerbit_match = re.search(patterns["penerbit"], all_text)
            penerbit = penerbit_match.group(0).strip() if penerbit_match else "N/A"

            # Extract 'doc_number'
            doc_number_match = re.search(patterns["doc_number"], all_text)
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
                "terbit_date": r"\b(?:[Dd]iterbitkan\s*pertama\s*tanggal|[Dd]iberikan\s*pertama\s*kali\s*pada|[Tt]anggal\s*:\s*|[Dd]itetapkan\s*di\s*\w+,?)\s*(\d{1,2})\s(\w+)\s(\d{4})",
                "validity_date": r"sampai(?:\s*dengan\s*tanggal)? (\d{1,2})\s([A-Za-z]+)\s(\d{4})",
                "validity_years": r"berlaku (?:untuk|paling lama) (\d+)",
                "nama": r"(?<=This is to certify that,\n)(.*)",
                "certificate_number": r"No\. Reg\.\s([A-Za-z0-9\s]+)(?=\n)",
                "competency": r"(?<=Competency:\n)(.*)"
            }

            # Extracting information using patterns
            masa_berlaku = {}
            tanggal_terbit = None

            # Extract tanggal terbit
            terbit_match = re.search(patterns["terbit_date"], all_text)
            if terbit_match:
                day, month_name, year = terbit_match.groups()
                tanggal_terbit = parse_date(day, month_name, year)
                masa_berlaku["tanggal_terbit"] = tanggal_terbit.strftime("%d-%m-%Y")

            # Extract validity dates
            for match in re.finditer(patterns["validity_date"], all_text):
                day, month_name, year = match.groups()
                formatted_date = parse_date(day, month_name, year).strftime("%d-%m-%Y")
                masa_berlaku[f"case_{match.start()}"] = formatted_date

            # Extract validity years and calculate expiration dates
            for match in re.finditer(patterns["validity_years"], all_text):
                years = int(match.group(1))
                expiration_date = tanggal_terbit + timedelta(days=365 * years)
                masa_berlaku[f"case_{match.start()}"] = expiration_date.strftime("%d-%m-%Y")

            # Extract additional fields
            nama = re.search(patterns["nama"], all_text).group(1).strip() if re.search(patterns["nama"], all_text) else None
            cert_number = re.search(patterns["certificate_number"], all_text).group(1).strip() if re.search(patterns["certificate_number"], all_text) else None
            competency = re.search(patterns["competency"], all_text).group(1).strip() if re.search(patterns["competency"], all_text) else None

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
                "ttl": r"Tempat\s*&\s*Tgl\.\s*Lahir\s*:\s*(.*)",
                "education": r"Pendidikan\s*:\s*(.*?)\s(.*?)\s*-\s*(\d{4})"
            }

            # Function to parse date strings
            def parse_date(date_str):
                return datetime.strptime(date_str, "%B %Y") if date_str != "Present" else datetime.now()

            # Extract personal details
            nama = re.search(patterns["nama"], all_text).group(1)
            ttl = re.search(patterns["ttl"], all_text).group(1)
            education = re.search(patterns["education"], all_text)
            univ, gelar, lulus = education.groups()

            # Parse experience entries
            experiences = []
            for date_range, role, project in re.findall(patterns["experience"], all_text):
                company_name = re.search(r"(.*)\n" + re.escape(date_range), all_text).group(1).strip()
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
            pattern = {"tanggal": r"Printed\s*On\s*:\s*(\d{2}-\w{3}-\d{4})|Tanggal\s*Penyampaian\s*:\s*(\d{2}/\d{2}/\d{4})|(\w+\s*\d{1,2},\s*\d{4})|Tanggal\s*:\s*(\d{2}\s*\w+\s*\d{4})",
                       "periode": r"FROM\s*:\s*(\d{4})|Tahun\s*Pajak\s*:\s*(\d{4})|yang\s*Berakhir\s*pada\s*.*?(\d{4})|sampai\s*dengan\s*tanggal\s*(\d{4})"
            }
            
            # Fungsi untuk memproses tanggal
            def process_date(match):
                if not any(match):  # Jika semua grup kosong, return None
                    return None
                
                try:
                    for i, group in enumerate(match):
                        if group:
                            if i == 0:  # Case 1: Format %d-%b-%Y
                                return datetime.strptime(group, "%d-%b-%Y").strftime("%d-%m-%Y")
                            elif i == 1:  # Case 2: Format %d/%m/%Y
                                return datetime.strptime(group, "%d/%m/%Y").strftime("%d-%m-%Y")
                            elif i == 2:  # Case 3: Month dd, yyyy
                                month, day, year = re.match(r"(\w+)\s*(\d{1,2}),\s*(\d{4})", group).groups()
                                return f"{int(day):02d}-{month_map[month]}-{year}"
                            elif i == 3:  # Case 4: dd Month yyyy
                                day, month, year = re.match(r"(\d{2})\s*(\w+)\s*(\d{4})", group).groups()
                                return f"{day}-{month_map[month]}-{year}"
                except Exception as e:
                    raise ValueError(f"Error processing date: {group}, {str(e)}")

            # Fungsi untuk memproses tahun
            def process_year(matches):
                try:
                    years = []
                    for idx, match in enumerate(matches):
                        extracted = [int(year) for year in match if year]
                        if idx == 2:  # Case 3: yang Berakhir pada ...
                            if extracted:
                                years.append(max(extracted))  # Ambil nilai maksimum
                        else:
                            years.extend(extracted)
                    return years
                except Exception as e:
                    raise ValueError(f"Error processing year: {str(e)}")

            # Ekstraksi
            try:
                tanggal_matches = re.findall(pattern["tanggal"], text)
                periode_matches = re.findall(pattern["periode"], text)

                # Proses data
                tanggal = [process_date(match) for match in tanggal_matches if any(match)]
                tahun = process_year(periode_matches)

                # Output JSON
                output = {
                    "error": None,
                    "tanggal": tanggal,
                    "tahun": tahun
                }
            except Exception as e:
                output = {
                    "error": str(e),
                    "tanggal": [],
                    "tahun": []
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
            pattern = {
                "nama": r"NPWP\s*:\s*\d{2}\.\d{3}\.\d{3}\.\d-\d{3}\.\d{3}\s*\n(.+)",
                "npwp": r"NPWP\s*:\s*(\d{2}\.\d{3}\.\d{3}\.\d-\d{3}\.\d{3})",
                "nik": r"NIK\s*:\s*(\d{16})",
                "kota": r"PROVINSI.*\n\n(.*)",
                "alamat": r"Alamat :.*?Kecamatan =.*",
            }
            
            nama = re.search(pattern["nama"], all_text).group(1) if re.search(pattern["nama"], all_text) else None
            npwp = re.search(pattern["npwp"], all_text).group(1) if re.search(pattern["npwp"], all_text) else None
            nik = re.search(pattern["nik"], all_text).group(1) if re.search(pattern["nik"], all_text) else None
            kota_match = re.search(pattern["kota"], all_text)
            kota = kota_match.group(1).strip() if kota_match else None

            # Ekstraksi bagian "Alamat" hingga "Kecamatan"
            alamat_match = re.search(pattern["alamat"], all_text, re.DOTALL)
            if alamat_match:
                section = alamat_match.group(0)  # Bagian yang ditemukan
                # Ekstraksi teks setelah ":" atau "="
                alamat_values = re.findall(r"[:=]\s*(.+)", section)
                alamat = ", ".join(alamat_values)
            else:
                alamat = None

            app.logger.warning("Unknown doc_type or sub_doc_type. No matching pattern.")
            output = {
                "error": "Unknown document type",
                "nama": nama,
                "npwp": npwp,
                "nik": nik,
                "alamat": f"{alamat}, {kota}"

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