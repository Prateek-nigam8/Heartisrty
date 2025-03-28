import argparse
import asyncio
import json
import pdfplumber
import pytesseract
import time
from pdf2image import convert_from_path
from dotenv import dotenv_values
from groq import AsyncGroq, RateLimitError
from httpx import HTTPStatusError

# Extraction prompt
PROMPT = """Extract the following integer fields from the medical report and return VALID JSON. Note that the report text may be poorly structured due to PDF extraction issues (for example, data from tables might be split across multiple lines). If a field is missing or cannot be reliably determined, omit it. If no fields are extracted, return an empty JSON object (i.e., {}):

- age: Patient's age.
- sex: (1 = Male, 0 = Female).
- cp: Chest pain type (0 = Typical, 1 = Atypical, 2 = Non-anginal, 3 = Asymptomatic).
- trestbps: Resting blood pressure (mm Hg).
- chol: Serum cholesterol (mg/dL).
- fbs: Fasting blood sugar indicator (mg/dL), where the value is 1 if the reported fasting blood sugar is greater than 120 mg/dl, otherwise 0.
- restecg: ECG (0 = Normal, 1 = ST-T abnormality, 2 = LVH).
- thal: Thalassemia (1 = Normal, 2 = Fixed defect, 3 = Reversible defect).
- triglycerides: Serum Triglyceride (mg/dL) (0 = Normal <150, 1 = Borderline 150–199, 2 = High 200–499, 3 = Very high ≥500).
"""

# Load environment variables
env_vars = dotenv_values(".env")
client = AsyncGroq(api_key=env_vars["GROQ_API_KEY"])
messages = [{"role": "system", "content": PROMPT}]


def is_scanned_pdf(pdf_path):
    """Check if a PDF is a scanned document (i.e., has no selectable text)."""
    with pdfplumber.open(pdf_path) as pdf:
        return not any(page.extract_text() for page in pdf.pages)


def extract_text_pdf(pdf_path):
    """Extract text from a PDF using pdfplumber."""
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                texts.append(text.strip())
    return texts


def extract_text_ocr(pdf_path):
    """Extract text from a scanned PDF using OCR (Tesseract)."""
    images = convert_from_path(pdf_path)
    return [pytesseract.image_to_string(img) for img in images]


def extract_text(pdf_path):
    """Decide whether to use pdfplumber or OCR to extract text."""
    return extract_text_ocr(pdf_path) if is_scanned_pdf(pdf_path) else extract_text_pdf(pdf_path)


async def process_page(page_text, index):
    """
    Send extracted text to the AI model and immediately retry on 429 or 500 errors.
    This function will retry indefinitely until a successful response is obtained.
    """
    while True:
        try:
            response = await client.chat.completions.create(
                messages=messages + [{"role": "user", "content": page_text}],
                model="llama3-70b-8192",
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return {k: v for k, v in data.items() if v is not None}

        except RateLimitError as e:
            retry_after = None
            if hasattr(e, "response") and e.response is not None:
                retry_after = e.response.headers.get("Retry-After")
            if retry_after:                
                await asyncio.sleep(float(retry_after))
            continue

        except HTTPStatusError as e:
            if e.response.status_code in (429, 500, 502, 503, 504, 400):
                retry_after = e.response.headers.get("Retry-After")
                if retry_after:
                    await asyncio.sleep(float(retry_after))
                continue
            else:
                raise

        except asyncio.CancelledError:
            # Instead of propagating, return an empty result for this page.
            return {}        


async def extract_medical_data_async(pdf_file):
    """
    Extract structured medical data asynchronously from a PDF.
    Each page is processed concurrently.
    """
    pages_text = extract_text(pdf_file)
    start_time = time.perf_counter()  # More precise timer than time.time()
    tasks = [process_page(page_text, i) for i, page_text in enumerate(pages_text)]
    
    results = await asyncio.gather(*tasks)
    end_time = time.perf_counter()
    print(f"Elapsed time: {end_time - start_time:.6f} seconds")

    final_result = {}
    for res in results:
        final_result.update(res)
    return final_result


def extract_medical_data(pdf_file, timeout=300):
    """
    Synchronous wrapper for the asynchronous extraction.
    If the process exceeds timeout seconds, a TimeoutError is raised.
    """
    return asyncio.run(
        asyncio.wait_for(extract_medical_data_async(pdf_file), timeout=timeout)
    )


def main():
    """CLI interface for running the script from the terminal."""
    parser = argparse.ArgumentParser(
        description="Extract structured data from a medical report PDF and return JSON."
    )
    parser.add_argument("pdf_file", help="Path to the PDF file")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds (default: 300)")
    args = parser.parse_args()

    result = extract_medical_data(args.pdf_file, timeout=args.timeout)
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()