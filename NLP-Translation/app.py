import threading
import time
from flask import Flask, request, render_template, send_file, jsonify, after_this_request
import pymupdf
from deep_translator import GoogleTranslator
import os

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
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    # Check if the file is a PDF
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "File is not a PDF"}), 400

    # Save the uploaded PDF temporarily
    input_path = "input_document.pdf"
    output_path = "translated_document.pdf"
    file.save(input_path)

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

    except Exception as e:
        return jsonify({"error": f"Failed to process the PDF: {str(e)}"}), 500
    finally:
        doc.close()

    # Schedule file deletion in a separate thread
    @after_this_request
    def remove_files(response):
        delayed_delete(input_path, output_path, delay=5)  # Delete files after 5 seconds
        return response

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
