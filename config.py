import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY not found. Please set it in your .env file. "
        "See .env.example for reference."
    )

MODEL_NAME = "gemini-3.5-flash"  # Update if a newer model is released

SYSTEM_PROMPT = """
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

MAX_FILE_SIZE_MB = 10
ALLOWED_TYPES = ["png", "jpg", "jpeg", "pdf"]
MAX_PDF_PAGES = 5
