import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
from google_api_key import google_api_key

# Configure Gemini
genai.configure(api_key=google_api_key)

# Load Model
model = genai.GenerativeModel("gemini-3.5-flash")

# System Prompt
system_prompt = """
You are a medical image analysis assistant.

Analyze only the uploaded medical image.

Provide the response under these headings:

1. Detailed Analysis
2. Analysis Report
3. Recommendations
4. Treatments

Important:
- Do not make a definitive diagnosis unless clearly visible.
- If the image quality is poor, mention it.
- If unsure, recommend further evaluation.
- Add this disclaimer:
'Consult with a Doctor before making any decisions.'
"""

# Streamlit UI
st.set_page_config(
    page_title="Visual Medical Assistant",
    page_icon="🩺",
    layout="wide"
)

st.title("Visual Medical Assistant 👨‍⚕️ 🩺 🏥")
st.subheader("Upload a Medical Image or PDF")

# File Upload
file_uploaded = st.file_uploader(
    "Upload Medical Image or PDF",
    type=["png", "jpg", "jpeg", "pdf"]
)

# Preview
if file_uploaded:

    if file_uploaded.type.startswith("image"):
        st.image(
            file_uploaded,
            width=300,
            caption="Uploaded Image"
        )

    elif file_uploaded.type == "application/pdf":
        st.success("PDF Uploaded Successfully")

# Button
submit = st.button("Generate Analysis")

if submit:

    if file_uploaded is None:
        st.warning("Please upload an image or PDF.")
        st.stop()

    try:

        # PDF Handling
        if file_uploaded.type == "application/pdf":

            pdf_bytes = file_uploaded.read()

            pdf_doc = fitz.open(
                stream=pdf_bytes,
                filetype="pdf"
            )

            first_page = pdf_doc.load_page(0)

            pix = first_page.get_pixmap()

            image_data = pix.tobytes("png")

            image_part = {
                "mime_type": "image/png",
                "data": image_data
            }

        # Image Handling
        else:

            image_data = file_uploaded.getvalue()

            image_part = {
                "mime_type": file_uploaded.type,
                "data": image_data
            }

        # Gemini Request
        response = model.generate_content([
            system_prompt,
            image_part
        ])

        st.subheader("Medical Analysis Report")
        st.write(response.text)

    except Exception as e:
        st.error(f"Error: {str(e)}")