from fastapi import UploadFile, File, Form
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase import create_client
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re
from datetime import datetime, timezone
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

load_dotenv()

router = APIRouter(prefix="/consent", tags=["Consent"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class ConsentRequest(BaseModel):
    patient_id: str
    language: str
    literacy_level: str
    consent_type: str
    notes: str | None = None


# ------------------------------------------------
# PDF CREATION (UNCHANGED)
# ------------------------------------------------
def create_pdf(patient_id, consent_text, language):

    filename = f"{patient_id}_consent.pdf"
    file_path = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(file_path)
    elements = []

    font_dir = os.path.join(os.getcwd(), "fonts")

    pdfmetrics.registerFont(
        TTFont("NotoEnglish", os.path.join(font_dir, "NotoSans-Regular.ttf"))
    )
    pdfmetrics.registerFont(
        TTFont("NotoHindi", os.path.join(font_dir, "NotoSansDevanagari-Regular.ttf"))
    )
    pdfmetrics.registerFont(
        TTFont("NotoMalayalam", os.path.join(font_dir, "NotoSansMalayalam-Regular.ttf"))
    )

    if language.lower() == "hindi":
        selected_font = "NotoHindi"
    elif language.lower() == "malayalam":
        selected_font = "NotoMalayalam"
    else:
        selected_font = "NotoEnglish"

    styles = getSampleStyleSheet()

    normal_style = ParagraphStyle(
        name="NormalUnicode",
        parent=styles["Normal"],
        fontName=selected_font,
        fontSize=11,
        leading=14,
    )

    heading_style = ParagraphStyle(
        name="HeadingUnicode",
        parent=styles["Heading1"],
        fontName=selected_font,
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue
    )

    subheading_style = ParagraphStyle(
        name="SubHeadingUnicode",
        parent=styles["Heading2"],
        fontName=selected_font,
        fontSize=13,
        spaceAfter=8,
        textColor=colors.black
    )

    lines = consent_text.split("\n")
    bullet_buffer = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)

        if line.startswith("# "):
            elements.append(Paragraph(line[2:], heading_style))
            elements.append(Spacer(1, 0.3 * inch))
            continue

        if line.startswith("## "):
            elements.append(Paragraph(line[3:], subheading_style))
            elements.append(Spacer(1, 0.2 * inch))
            continue

        if line.startswith("- "):
            bullet_buffer.append(
                ListItem(Paragraph(line[2:], normal_style))
            )
            continue
        else:
            if bullet_buffer:
                elements.append(ListFlowable(bullet_buffer, bulletType="bullet"))
                elements.append(Spacer(1, 0.2 * inch))
                bullet_buffer = []

        elements.append(Paragraph(line, normal_style))
        elements.append(Spacer(1, 0.2 * inch))

    if bullet_buffer:
        elements.append(ListFlowable(bullet_buffer, bulletType="bullet"))

    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("Doctor Signature: ____________________", normal_style))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Patient Signature: ____________________", normal_style))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Date: ____________________", normal_style))

    doc.build(elements)

    return filename


# ------------------------------------------------
# GENERATE CONSENT (OPTIMIZED VERSION)
# ------------------------------------------------
@router.post("/generate")
async def generate_consent(data: ConsentRequest):
    try:
        print("🔵 Received request:", data)

        # -------------------------------
        # Structured Extraction (1st GPT call)
        # -------------------------------
        structured_prompt = f"""
Convert the following clinical notes into structured JSON.

Extract:
- pregnancy_status
- trimester
- diabetes_status
- comorbidities
- symptoms
- risk_flags

Return ONLY valid JSON.

Notes:
{data.notes}
"""

        structured_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": structured_prompt}],
            temperature=0
        )

        structured_content = structured_response.choices[0].message.content.strip()

        if structured_content.startswith("```"):
            structured_content = structured_content.replace("```json", "").replace("```", "").strip()

        structured_summary = json.loads(structured_content)

        # -------------------------------
        # Language Handling
        # -------------------------------
        lang_key = data.language.strip().lower()

        fixed_titles = {
            "english": "Informed Consent Form",
            "hindi": "सूचित सहमति पत्र",
            "malayalam": "അറിവുള്ള സമ്മത ഫോം"
        }

        main_title = fixed_titles.get(lang_key, fixed_titles["english"])

        section_headings = {
            "english": [
                "Introduction & Purpose",
                "Why You Are Invited",
                "Study Procedures",
                "Risks & Possible Side Effects",
                "Potential Benefits",
                "Alternatives",
                "Confidentiality & Data Protection",
                "Costs & Compensation",
                "Voluntary Participation",
                "Right to Withdraw",
                "Contact Information",
                "Statement of Consent"
            ],
            "hindi": [
                "परिचय एवं उद्देश्य",
                "आपको क्यों आमंत्रित किया गया है",
                "अध्ययन प्रक्रिया",
                "जोखिम एवं संभावित दुष्प्रभाव",
                "संभावित लाभ",
                "विकल्प",
                "गोपनीयता एवं डेटा सुरक्षा",
                "लागत एवं मुआवजा",
                "स्वैच्छिक भागीदारी",
                "अध्ययन से हटने का अधिकार",
                "संपर्क जानकारी",
                "सहमति का वक्तव्य"
            ],
            "malayalam": [
                "പരിചയം & ഉദ്ദേശ്യം",
                "നിങ്ങളെ ക്ഷണിച്ചതിന്റെ കാരണം",
                "പഠന നടപടികൾ",
                "സാധ്യതയുള്ള അപകടങ്ങളും പാർശ്വഫലങ്ങളും",
                "സാദ്ധ്യതയുള്ള നേട്ടങ്ങൾ",
                "മാറ്റുവഴികൾ",
                "റഹസ്യതയും ഡാറ്റ സംരക്ഷണവും",
                "ചെലവും നഷ്ടപരിഹാരവും",
                "സ്വമേധയാ പങ്കെടുക്കൽ",
                "പിന്മാറാനുള്ള അവകാശം",
                "ബന്ധപ്പെടാനുള്ള വിവരങ്ങൾ",
                "സമ്മത പ്രസ്താവന"
            ]
        }

        sections = section_headings.get(lang_key, section_headings["english"])

        language_instruction = {
            "english": "Write entirely in clear natural English.",
            "hindi": "Write entirely in fluent Hindi using only Devanagari script.",
            "malayalam": "Write entirely in fluent Malayalam using only Malayalam script."
        }

        # -------------------------------
        # NEW: Literacy Level Instructions
        # -------------------------------
        literacy_instruction = ""

        if data.literacy_level.lower() == "simple":
            literacy_instruction = """
Write the consent form for patients with low health literacy.

Rules:
- Use simple everyday language
- Keep sentences short and easy to understand
- Avoid complex medical terminology
- If medical terms appear, explain them in simple words
- Use bullet points where appropriate
- Maintain a friendly and reassuring tone
- Expand explanations so the final document fills approximately 3 pages
"""

        elif data.literacy_level.lower() == "technical":
            literacy_instruction = """
Write the consent form in a professional clinical research tone.

Rules:
- Use formal medical terminology
- Explain the pharmacological mechanisms of Metformin, Sitagliptin, and Empagliflozin
- Describe the study design, screening procedures, and monitoring protocols
- Explain clinical endpoints and possible adverse effects
- Use structured paragraphs rather than simple bullet points
- Expand explanations so the final document fills approximately 3 pages
"""

        # -------------------------------
        # FULL CONSENT GENERATION (2nd GPT call ONLY)
        # -------------------------------
        full_prompt = f"""
Write a complete informed consent form.

IMPORTANT LENGTH REQUIREMENT:
The document must contain enough detailed content to fill approximately
3 pages when converted to a PDF.

{literacy_instruction}

Use EXACTLY these section headings in this exact order:

{sections}

Rules:
- Do NOT add extra headings
- Stay strictly within a Type 2 Diabetes clinical trial context
- Study drugs: Metformin, Sitagliptin, Empagliflozin ONLY
- Do not mention any other drugs
- Minimum word count: 1200 words

Patient ID: {data.patient_id}

Structured Clinical Summary:
{structured_summary}

{language_instruction.get(lang_key, "Write in English.")}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.3
        )

        consent_body = response.choices[0].message.content.strip()

        consent_text = f"# {main_title}\n\n{consent_body}"

        # -------------------------------
        # Create PDF
        # -------------------------------
        filename = create_pdf(data.patient_id, consent_text, data.language)

        # -------------------------------
        # Store in Supabase
        # -------------------------------
        supabase.table("consents").insert({
            "patient_id": data.patient_id,
            "language": data.language,
            "literacy_level": data.literacy_level,
            "notes_text": data.notes,
            "structured_summary": structured_summary,
            "consent_generated_url": filename,
            "consented": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()

        return {
            "message": "Consent generated",
            "download_url": f"http://localhost:5000/outputs/{filename}",
            "structured_summary": structured_summary
        }

    except Exception as e:
        print("🔴 ERROR OCCURRED:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/upload-signed")
async def upload_signed_consent(
    patient_id: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files allowed")

        # Unique file name
        file_name = f"{patient_id}_signed_{datetime.now().timestamp()}.pdf"

        file_bytes = await file.read()

        # Upload to Supabase Storage bucket
        supabase.storage.from_("signed_consents").upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": "application/pdf"}
        )

        # Get public URL
        public_url = supabase.storage.from_("signed_consents").get_public_url(file_name)

        # Update consents table
        supabase.table("consents") \
            .update({
                "signed_consent_url": public_url,
                "consented": True,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }) \
            .eq("patient_id", patient_id) \
            .execute()

        return {
            "message": "Signed consent uploaded successfully",
            "signed_url": public_url
        }

    except Exception as e:
        print("🔴 Signed upload error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))