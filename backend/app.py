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
        for page_number in range(doc.page_count):
            page = doc.load_page(page_number)
            lines = page.get_text("text").split('\n')

            # Get the first line matching the heading criteria
            heading_line = self.get_heading(lines)

            if heading_line:
                # Replace the heading text with a mask (e.g., '[MASKED]')
                lines[0] = lines[0].replace(heading_line, '[MASKED]')

            # Continue with the redaction logic for the rest of the page

        redacted_filename = f'redacted_{pdf_file.filename}'
        redacted_path = os.path.join(output_dir, redacted_filename)
        doc.save(redacted_path)
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
