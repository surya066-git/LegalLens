from __future__ import annotations

import io

import pymupdf


EMPLOYMENT_CONTRACT = """EMPLOYMENT AGREEMENT

1. Notice Period
Either party may terminate this agreement with 30 days written notice
unless another period is expressly required by applicable policy or law.

2. Probation
The employee shall serve a probationary period of six months from the commencement date.

3. Compensation
The employee will receive an annual salary of 90,000 USD, payable monthly.

4. Confidentiality
The employee shall keep confidential all proprietary information of the company during employment and for two years afterwards.

5. Non-Compete
The employee shall not join a competing business within 6 months after termination in the same city.

6. Working Hours
Normal working hours are 9:00 to 17:30 Monday to Friday.
"""


def pdf_bytes_from_text(text: str, pages: int = 1) -> bytes:
    document = pymupdf.open()
    try:
        for index in range(pages):
            page = document.new_page()
            page.insert_text((72, 72), text if index == 0 else f"Continuation page {index + 1}")
        return document.tobytes()
    finally:
        document.close()


def employment_pdf() -> bytes:
    return pdf_bytes_from_text(EMPLOYMENT_CONTRACT)


def upload_file_tuple(filename: str, data: bytes, content_type: str = "application/pdf"):
    return {"file": (filename, io.BytesIO(data), content_type)}
