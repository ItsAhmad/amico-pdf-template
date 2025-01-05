from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from boxsdk import Client, OAuth2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import config

app = Flask(__name__)

CLIENT_ID = 'client_id_config' 
CLIENT_SECRET = 'client_secret_config'
DEVELOPER_TOKEN = 'developer_token_config'

oauth2 = OAuth2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, access_token=DEVELOPER_TOKEN)
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
    file_name_mario = 'MARIO KULIS.PDF'
    file_name_kareem = 'KAREEM KAMAL.PDF'
    file_name_john = 'JOHN LY.PDF'
    file_name_stefani = 'STEFANI EROGULLARI.pdf'
    items = client.folder(folder_id).get_items()
    file_id = next(item.id for item in items if item.name == file_name)

    box_file = client.file(file_id).content()

     # Create overlay with dynamic content
    overlay_stream = io.BytesIO()
    c = canvas.Canvas(overlay_stream, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 500, f"Client Name: {client_name}")
    c.drawString(100, 480, f"Message: {message}")
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
    return send_file(output_stream, as_attachment=True, download_name=f"{salesperson}_customized.pdf")

if __name__ == '__main__':
    app.run()