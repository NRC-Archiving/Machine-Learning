import threading
import time
from flask import Flask, request, render_template, send_file, jsonify, after_this_request
import pymupdf
from deep_translator import GoogleTranslator
import os
import threading
import time

# Load env
from dotenv import load_dotenv
load_dotenv()
host = os.getenv('HOST_SERVER') or '127.0.0.1'
port = os.getenv('PORT_SERVER') or 5000
brokers = os.getenv('BROKERS')

# Initialize Kafka broker
from kafka_prod import KafkaProducerClient
from kafka_consum import KafkaConsumerClient
kafka_producer = KafkaProducerClient(bootstrap_servers=[brokers])
kafka_consumer_translation = KafkaConsumerClient(topic="translation_results", bootstrap_servers=[brokers])

# Handle translation results with brokers
translations = {}
def handle_translation_results(data):
    result = data.get("message")
    req_id = result.get("req_id")

    if not req_id:
        print("Received message without req_id, ignoring...")
        return
    
    if "error" in result:
        print("Error in translation request: ", result.get("error"))
        translations[req_id] = {"status":"failed","error": result.get("error")}
        return
    else:
        print("Received translation result: id[", req_id, "]")
        translations[req_id] = {"status":"completed", "output_path": result.get("output_path")}
        return
kafka_consumer_translation.start_listening(handle_translation_results)

# Set folder for temporary files
TEMP_FOLDER = "temp"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)

# Define translator and color "white"
WHITE = pymupdf.pdfcolor["white"]
to_english = GoogleTranslator(source="id", target="en")

def delayed_delete(*files, delay=5):
    """Delete files after a delay to ensure they are no longer in use."""
    def delete_files():
        time.sleep(delay)  # Wait before attempting deletion
        for file in files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"Deleted: {file}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")
    
    threading.Thread(target=delete_files, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate_pdf', methods=['POST'])
def translate_pdf():
    requester_id = request.form.get('requester_id', 'unknown')

    if not requester_id:
        return jsonify({"error": "No requester_id provided"}), 400

    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    # Check if the file is a PDF
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "File is not a PDF"}), 400

    # Save the uploaded PDF temporarily
    req_id = str(int(time.time()))
    input_path = f"{TEMP_FOLDER}/input_document-{req_id}.pdf"
    output_path = f"{TEMP_FOLDER}/translated_document-{req_id}.pdf"
    file.save(input_path)

    kafka_producer.send_result("translation_requests", True, {
        "req_id": req_id,
        "requester_id": requester_id,
        "filename": file.filename
    })

    # Open the PDF with pymupdf
    try:
        # Open the PDF with pymupdf
        doc = pymupdf.open(input_path)
        textflags = pymupdf.TEXT_DEHYPHENATE

        # Create Optional Content layer named "Indonesian" and activate it
        ocg_xref = doc.add_ocg("Indonesian", on=True)

        # Iterate over all pages for translation
        for page in doc:
            blocks = page.get_text("dict", flags=textflags)["blocks"]
            
            for block in blocks:
                for line in block["lines"]:
                    for span in line["spans"]:
                        bbox = span["bbox"]
                        text = span["text"]
                        font = span["font"]
                        flags = span["flags"]

                        # Translate the text
                        english_text = to_english.translate(text)
                        
                        # Cover original text with white rectangle
                        page.draw_rect(bbox, color=None, fill=WHITE, oc=ocg_xref)

                        # Prepare HTML string with style information
                        style = f"font-family: {font};"
                        if flags & 2**0:
                            style += "vertical-align: super;"
                        if flags & 2**1:
                            style += "font-style: italic;"
                        if flags & 2**3:
                            style += "font-family: monospace;"
                        if flags & 2**4:
                            style += "font-weight: bold;"

                        html = f'<span style="{style}">{english_text}</span>'
                        
                        # Insert the translated HTML content
                        page.insert_htmlbox(bbox, html, oc=ocg_xref)

        # Subset fonts and save the output file
        doc.subset_fonts()
        doc.ez_save(output_path)

        kafka_producer.send_result("translation_results", True, {
            "req_id": req_id,
            "requester_id": requester_id,
            "output_path": output_path
        })

    except Exception as e:
        kafka_producer.send_result("translation_results", False, {
            "req_id": req_id,
            "requester_id": requester_id,
            "error": str(e)
        })

        return jsonify({"error": f"Failed to process the PDF: {str(e)}"}), 500
    finally:
        doc.close()

    # Schedule file deletion in a separate thread
    @after_this_request
    def remove_files(response):
        delayed_delete(input_path, output_path, delay=5)  # Delete files after 5 seconds
        return response

    return send_file(output_path, as_attachment=True)

# Route to get translation status
@app.route('/translate_pdf/status/<req_id>', methods=['GET'])
def get_translation_status(req_id):
    result = translations.get(req_id)

    if not result:
        return jsonify({"status": "pending"}), 200

    if result["status"] == "failed":
        return jsonify({"status": "failed", "error": result["error"]}), 500

    return jsonify({"status": "completed", "download_url": f"/translate_pdf/{req_id}"}), 200

# Route to download translated pdf
@app.route('/translate_pdf/<req_id>', methods=['GET'])
def download_translated_pdf(req_id):
    result = translations.get(req_id)

    if not result or "output_path" not in result:
        return jsonify({"error": "File not found or still processing"}), 404

    output_path = result["output_path"]
    if not os.path.exists(output_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host=host, port=port, debug=True)
