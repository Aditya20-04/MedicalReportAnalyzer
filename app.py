import streamlit as st
import google.generativeai as genai

from config import (
    GOOGLE_API_KEY,
    MODEL_NAME,
    SYSTEM_PROMPT,
    MAX_FILE_SIZE_MB,
    ALLOWED_TYPES,
    MAX_PDF_PAGES,
)
from utils import (
    validate_file_size,
    extract_images_from_pdf,
    prepare_image_part,
    is_valid_pdf,
)

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# Streamlit Page Config
st.set_page_config(
    page_title="Visual Medical Assistant",
    page_icon="🩺",
    layout="wide"
)

st.title("Visual Medical Assistant 👨‍⚕️ 🩺 🏥")
st.subheader("Upload a Medical Image or PDF")

st.info(
    "⚠️ This tool provides AI-generated insights for informational purposes only. "
    "It is **NOT** a substitute for professional medical diagnosis. "
    "Always consult a licensed doctor before making any decisions."
)

# File Upload
file_uploaded = st.file_uploader(
    "Upload Medical Image or PDF",
    type=ALLOWED_TYPES
)

# Validate size immediately after upload
if file_uploaded and not validate_file_size(file_uploaded, MAX_FILE_SIZE_MB):
    st.error(f"File too large. Please upload a file under {MAX_FILE_SIZE_MB}MB.")
    st.stop()

# Preview
if file_uploaded:
    if file_uploaded.type.startswith("image"):
        st.image(file_uploaded, width=300, caption="Uploaded Image")
    elif file_uploaded.type == "application/pdf":
        st.success("PDF Uploaded Successfully")

# Generate Analysis
submit = st.button("Generate Analysis", type="primary")

if submit:
    if file_uploaded is None:
        st.warning("Please upload an image or PDF.")
        st.stop()

    try:
        with st.spinner("Analyzing medical image... this may take a few seconds"):

            image_parts_to_send = []

            # PDF Handling — multi-page support
            if file_uploaded.type == "application/pdf":
                pdf_bytes = file_uploaded.read()

                if not is_valid_pdf(pdf_bytes):
                    st.error("The uploaded PDF appears to be corrupted or unreadable.")
                    st.stop()

                image_parts, total_pages = extract_images_from_pdf(
                    pdf_bytes, max_pages=MAX_PDF_PAGES
                )

                if total_pages > MAX_PDF_PAGES:
                    st.warning(
                        f"PDF has {total_pages} pages. "
                        f"Only the first {MAX_PDF_PAGES} were analyzed."
                    )

                image_parts_to_send = [
                    {"mime_type": p["mime_type"], "data": p["data"]}
                    for p in image_parts
                ]

            # Image Handling
            else:
                image_data = file_uploaded.getvalue()
                image_parts_to_send = [
                    prepare_image_part(image_data, file_uploaded.type)
                ]

            # Build content: prompt + all image parts
            content = [SYSTEM_PROMPT] + image_parts_to_send

            # Gemini Request
            response = model.generate_content(content)

        st.subheader("Medical Analysis Report")
        st.write(response.text)

        st.download_button(
            label="📥 Download Report",
            data=response.text,
            file_name="medical_analysis_report.txt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        st.info("Please try again with a different file or check your internet connection.")

# Footer
st.markdown("---")
st.caption(
    "Visual Medical Assistant uses Google Gemini for AI-powered image analysis. "
    "No uploaded data is stored by this application."
)
