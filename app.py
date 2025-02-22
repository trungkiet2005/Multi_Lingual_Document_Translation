import streamlit as st
import base64
from translate_use_api import translated_pdf
import io
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from pdf2image import convert_from_bytes

def pdf_bytes_to_image_bytes(pdf_bytes):
    images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)  # Chỉ lấy trang đầu tiên

    if images:
        img_bytes = io.BytesIO()
        images[0].save(img_bytes, format="JPEG")  # Lưu ảnh vào bytes
        return img_bytes.getvalue()  # Trả về bytes của ảnh
    return None

def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    
    st.markdown(pdf_display, unsafe_allow_html=True)

def display_txt_code(txt_bytes):
    text = txt_bytes.decode("utf-8")
    st.code(text, language="plaintext")
    
    
def convert_image_to_pdf(image_bytes):
    # Create a bytes buffer for the PDF
    pdf_buffer = io.BytesIO()
    
    # Open the image using PIL
    image = Image.open(io.BytesIO(image_bytes))
    
    # Convert RGBA to RGB if necessary
    if image.mode == 'RGBA':
        image = image.convert('RGB')
    
    # Get original image dimensions in pixels
    img_width, img_height = image.size
    
    # Convert pixels to points (72 points = 1 inch)
    # Assuming standard screen resolution of 96 DPI
    pdf_width = img_width * 72.0 / 96.0
    pdf_height = img_height * 72.0 / 96.0
    
    # Create PDF with custom page size to match image dimensions
    custom_pagesize = (pdf_width, pdf_height)
    c = canvas.Canvas(pdf_buffer, pagesize=custom_pagesize)
    
    # Draw the image at full size
    temp_img = io.BytesIO(image_bytes)
    temp_img.seek(0)
    c.drawImage(ImageReader(temp_img), 0, 0, width=pdf_width, height=pdf_height)
    c.save()
    
    return pdf_buffer.getvalue()

def main():
    st.title("Deploying a Multi Lingual Document Translator App")
    st.write("This is a simple app to translate documents from one language to another. It uses google cloud translate API to perform the translation.")
    
    uploaded_file = st.file_uploader("Upload a document for translation", 
                                     type=['pdf', 'jpg', 'png'])
    
    if uploaded_file is not None:
        st.success("File uploaded successfully.")
        st.write("This is the content of the file you uploaded.")
        
        file_bytes = uploaded_file.read()
        
        if "image" not in uploaded_file.type:
            display_pdf(file_bytes)
            pdf_bytes = file_bytes
        else:
            # Display the image
            image = Image.open(io.BytesIO(file_bytes))
            st.image(image, caption="Uploaded Image", use_container_width=True)
            # Convert image to PDF
            pdf_bytes = convert_image_to_pdf(file_bytes)
            
        source_language = st.selectbox("Select the source language", 
                                     options=["VietNamese", "French", "Spanish", "English", "Chinese"])
        
        target_language = st.selectbox("Select the target language", 
                                     options=["English", "French", "Spanish", "VietNamese", "Chinese"])

        if st.button("Translate"):
            source_language = source_language.lower()[:2]
            target_language = target_language.lower()[:2]
            # Use the PDF bytes for translation
            file_name = uploaded_file.name.replace(".jpg", ".pdf")
            file_name = file_name.replace(".png", ".pdf")
            translate_file = translated_pdf(file_name, pdf_bytes, 
                                            source_language, target_language)
            
            st.success("File translated successfully.")
            if "image" not in uploaded_file.type:
                display_pdf(translate_file)
            else:
                image_bytes = pdf_bytes_to_image_bytes(translate_file)
                image = Image.open(io.BytesIO(image_bytes))
                st.image(image, caption="Translated Image", use_container_width=True)
                
            
if __name__ == '__main__':
    main()
