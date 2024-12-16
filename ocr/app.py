import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from preprocessors.pdf_preprocessor import preprocess_pdf_and_extract_text
from extractors import (
    extract_legalitas,
    extract_tenaga_ahli,
    extract_kontrak,
    extract_cv,
    extract_keuangan,
    extract_surat_masuk,
    extract_surat_keluar,
    extract_pengurus_pemegang_saham
)

# Initialize Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

def allowed_file(filename):
    """
    Check if a file has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/extract', methods=['POST'])
def extract_document():
    doc_type = request.form.get('doc_type', 'unknown')
    crop_ratio = float(request.form.get('crop_ratio', 0.2))
    remove_lines = request.form.get('remove_lines', 'false').lower() == 'true'
    preprocessing_method = request.form.get('preprocessing_method', 'trunc')
    file = request.files.get('file')

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid or missing file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        output_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'processed')
        os.makedirs(output_folder, exist_ok=True)

        # Extract text from the PDF
        extracted_text = preprocess_pdf_and_extract_text(
            pdf_path=file_path,
            output_folder=output_folder,
            crop_ratio=crop_ratio,
            doc_type=doc_type,
            preprocessing_method=preprocessing_method,
            remove_lines=remove_lines
        )

        # Route to appropriate extractor
        extractors = {
            "legalitas": extract_legalitas,
            "tenaga_ahli": extract_tenaga_ahli,
            "kontrak": extract_kontrak,
            "cv": extract_cv,
            "keuangan": extract_keuangan,
            "surat_masuk": extract_surat_masuk,
            "surat_keluar": extract_surat_keluar,
            "pengurus": extract_pengurus_pemegang_saham,
            "pemegang_saham": extract_pengurus_pemegang_saham
        }

        if doc_type in extractors:
            result = extractors[doc_type](extracted_text)
        else:
            result = {"error": f"Unknown document type: {doc_type}"}

    except Exception as e:
        result = {"error": f"An error occurred: {str(e)}"}

    finally:
        # Cleanup the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
