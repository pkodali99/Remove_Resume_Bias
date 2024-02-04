# imports
import fitz
import os
import re
from flask_cors import CORS
from flask import Flask, send_from_directory, jsonify, request

app = Flask(__name__, static_folder="dist/my-app")
CORS(app)
# Class to represent your redaction API
class Redactor:
    @staticmethod
    def get_heading(lines):
        """ Function to get the first line matching the heading criteria """
        HEADING_REG = r"^[A-Z][a-z]*\s[\w'’-]+(?:\s[\w'’-]+)*$"

        for line in lines:
            search = re.search(HEADING_REG, line)
            if search:
                return search.group(0)

    def redaction(self, pdf_file, output_dir='redacted_pdfs'):
        os.makedirs(output_dir, exist_ok=True)

        # Save the uploaded file to the 'uploads' directory
        pdf_path = os.path.join(output_dir, pdf_file.filename)
        pdf_file.save(pdf_path)

        doc = fitz.open(pdf_path)
        for page in doc:
            # Find text blocks and their font sizes
            text_blocks = page.get_text("dict")["blocks"]
            largest_font_size = 0
            largest_text = None

            # Determine the largest font size and corresponding text
            for block in text_blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span["size"] > largest_font_size:
                                largest_font_size = span["size"]
                                largest_text = span["text"]

            # Mask the text with the largest font
            if largest_text:
                for block in text_blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                if span["text"] == largest_text:
                                    rect = fitz.Rect(span["bbox"])
                                    page.add_redact_annot(rect, fill=(0, 0, 0))  # Black color mask

        page.apply_redactions()

        # Continue with the redaction logic for the rest of the page

        redacted_filename = f'redacted_{pdf_file.filename}'
        redacted_path = os.path.join(output_dir, redacted_filename)
        doc.save(redacted_path)
        doc.close()
        print(f"Successfully redacted. Redacted PDF saved at: {redacted_path}")
        return redacted_path

# Routes for serving Angular app and handling redaction
@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/api/redact', methods=['POST'])
def catch_all(path=None):
    if request.method == 'POST':
        try:
            print("Req in backend")
            pdf_file = request.files['pdfFile']
            print(f"Received PDF file: {pdf_file.filename}")
            redactor = Redactor()
            redacted_path = redactor.redaction(pdf_file, output_dir='redacted_pdfs')
            print(f"Redacted PDF saved at: {redacted_path}")
            return send_from_directory('.', redacted_path, as_attachment=True)
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify(error=str(e)), 500
    elif path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)
