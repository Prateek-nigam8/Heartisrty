import argparse
import asyncio
import json
import pdfplumber
import pytesseract
import time
from pdf2image import convert_from_path
from dotenv import dotenv_values
from groq import AsyncGroq, RateLimitError, BadRequestError
from httpx import HTTPStatusError

# Extraction prompt
PROMPT = """Extract JSON with these keys exactly:
- Age: integer (years)
- Sex: "Male" or "Female"
- ChestPainType: one of
    • TA = Typical Angina
    • ATA = Atypical Angina
    • NAP = Non-anginal Pain
    • ASY = Asymptomatic
- RestingBP: integer (mm Hg)
- Cholesterol: integer (mg/dL)
- FastingBS: integer (mg/dL)
- RestingECG: one of
    • Normal
    • ST = ST-T wave abnormality
    • LVH = Left ventricular hypertrophy
- MaxHR: integer (beats per minute)
- ExerciseAngina: "Yes" or "No"
- Oldpeak: decimal (ST depression vs. rest)
- ST_Slope: one of
    • Up = upward slope
    • Flat = flat slope
    • Down = downward slope

If a field is missing or unclear, omit it.  
If none are found, return {}.
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

        except BadRequestError as e:
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