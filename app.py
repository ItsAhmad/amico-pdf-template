from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from boxsdk import OAuth2, Client
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import fonts
import io
import os

app = Flask(__name__)

CLIENT_ID = os.getenv("client_id_config")
CLIENT_SECRET = os.getenv("client_secret_config")
DEVELOPER_TOKEN = os.getenv("developer_token_config")

oauth2 = OAuth2(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    access_token=DEVELOPER_TOKEN,
)

client = Client(oauth2)


@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    # Extract user data from the form
    RSM = request.form.get('RSM')
    date = request.form.get('date')
    contactName = request.form.get('contactName')
    contactAddy = request.form.get('contactAddy')
    message = request.form.get('message')

    folder_id = '301251997812'
    rsm_to_file_map = {
    "KK": "KAREEM KAMAL.pdf",
    "MK": "MARIO KULIS.pdf",
    "JL": "JOHN LY.pdf",
    "SE": "STEFANI EROGULLARI.pdf",
    "AA": "AHMAD AMEEN.PDF",
    }

    file_name = rsm_to_file_map.get(RSM)

    if not file_name:
      return "Invalid salesperson selected.", 400

    items = client.folder(folder_id).get_items()
    file_id = next((item.id for item in items if item.name == file_name), None)

    if not file_id:
      return f"Template for {file_name} not found.", 404

    box_file = client.file(file_id).content()

     # Create overlay with dynamic content
    fonts.addMapping('MyriadPro-Light', 0, 0, 'fonts/MyriadPro-Light.otf')
    overlay_stream = io.BytesIO()
    c = canvas.Canvas(overlay_stream, pagesize=letter)
    c.setFont('MyriadPro-Light', 14)

    words = message.split()
    wrap_width = 200
    current_line = ""
    lines = []

    for word in words: 
        test_line = f"{current_line} {word}".strip()
        if c.stringWidth(test_line, "MyriadPro-Light", 12) <= wrap_width:
            current_line = test_line
        else: 
            lines.append(current_line)
            current_line = word
    if current_line: 
        lines.append(current_line)

    line_height = 14
    y_position = 570

    for line in lines:
        c.drawString(300, y_position , line) 
        y_position -= line_height 
       
    c.drawString(300, 669, f"{contactName}")
    c.drawString(300, 650, f"{date}")
    c.drawString(300, 630, f"{contactAddy}")
    c.save()
    overlay_stream.seek(0)

    # Merge overlay with the template
    base_pdf = PdfReader(io.BytesIO(box_file))
    overlay_pdf = PdfReader(overlay_stream)
    writer = PdfWriter()

    for page in base_pdf.pages:
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

    # Save the final PDF to a stream
    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)

    # Return the generated PDF for download
    return send_file(output_stream, as_attachment=True, download_name=f"{RSM}_customized.pdf")

if __name__ == '__main__':
    app.run()