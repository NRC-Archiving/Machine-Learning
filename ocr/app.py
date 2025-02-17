import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from preprocessors.pdf_preprocessor import extract_text_from_pdf  # ✅ Uses Hybrid Optimization
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
import asyncio

# Load env
from dotenv import load_dotenv
load_dotenv()
host = os.getenv('HOST_SERVER') or '127.0.0.1'
port = os.getenv('PORT_SERVER') or 5000
brokers = os.getenv('BROKERS') or 'localhost:9092'

# Initialize Kafka broker
from kafka_prod import KafkaProducerClient
kafka_client = KafkaProducerClient(
    bootstrap_servers=[brokers],
    topic="test-topic"
)

# Initialize Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/extract', methods=['POST'])
def extract_document():
    doc_type = request.form.get('doc_type', 'unknown')
    doc_id = request.form.get('doc_id', 'none')
    file = request.files.get('file')

    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid or missing file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        # ✅ Extract text using the Hybrid Optimized OCR Pipeline
        extracted_text = extract_text_from_pdf(file_path, doc_type=doc_type)

        # ✅ Dictionary mapping document types to their respective extractors
        extractors = {
            "legalitas": extract_legalitas,
            "tenaga_ahli": extract_tenaga_ahli,
            "kontrak": extract_kontrak,
            "cv": extract_cv,
            "keuangan": extract_keuangan,
            "surat_masuk": extract_surat_masuk,
            "surat_keluar": extract_surat_keluar,
            "pengurus": lambda text: extract_pengurus_pemegang_saham(text, doc_type="pengurus"),
            "pemegang_saham": lambda text: extract_pengurus_pemegang_saham(text, doc_type="pemegang_saham")
        }

        # ✅ Use the appropriate extractor for the document type
        if doc_type in extractors:
            result = extractors[doc_type](extracted_text)
        else:
            result = {"error": f"Unknown document type: {doc_type}"}

    except Exception as e:
        result = {"error": f"An error occurred: {str(e)}"}

    finally:
        # ✅ Remove the uploaded file after processing
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Send result to message broker
    data = { "doc_id": doc_id, "doc_type": doc_type, "result": result }
    kafka_client.send_result(True, data)

    return jsonify(result)

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
