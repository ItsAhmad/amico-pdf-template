from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from boxsdk import Client, OAuth2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
from boxsdk import OAuth2, Client

app = Flask(__name__)

oauth2 = OAuth2(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    store_tokens=lambda access_token, refresh_token: print(f"New tokens: {access_token}, {refresh_token}")
)

auth_url, csrf_token = oauth2.get_authorization_url('https://amico.box.com')
print(f"Visit this URL to authorize the app: {auth_url}")

oauth2.authenticate('authorization_code')



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
    "KK": "KAREEM KAMAL.PDF",
    "MK": "MARIO KULIS.PDF",
    "JL": "JOHN LY.PDF",
    "SE": "STEFANI EROGULLARI.PDF",
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
    overlay_stream = io.BytesIO()
    c = canvas.Canvas(overlay_stream, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 500, f"contact name:{contactName}")
    c.drawString(100, 490, f"Date:{date}")
    c.drawString(100, 495, f"Address:{contactAddy}")
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
    return send_file(output_stream, as_attachment=True, download_name=f"{RSM}_customized.pdf")

if __name__ == '__main__':
    app.run()