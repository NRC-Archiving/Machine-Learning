from flask import Flask, request, render_template, send_file, jsonify
import pymupdf 
from deep_translator import GoogleTranslator
from deep_translator import MyMemoryTranslator
import os

# Initialize Flask app
app = Flask(__name__)

# Define translator and color "white"
WHITE = pymupdf.pdfcolor["white"]
to_english = MyMemoryTranslator(source="id-ID", target="en-US")

# Route to display the HTML form for file upload
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle PDF upload and translation
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

    # Open the PDF with pymupdf
    try:
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

    # Send the processed PDF file back to the client
    return send_file(output_path, as_attachment=True)

# Start Flask app
if __name__ == '__main__':
    app.run(debug=True)