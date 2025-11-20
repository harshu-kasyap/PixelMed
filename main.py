import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import base64
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
import re
from datetime import datetime

# ------------------------------------
# CONFIGURE GOOGLE API
# ------------------------------------
GOOGLE_API_KEY = "AIzaSyCb-lkObsyDqVUPW78vwLSnHX6M0AvCFzc"
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")


# ------------------------------------
# PDF GENERATION FUNCTION
# ------------------------------------
def create_pdf_report(report_text, image_path, filename):
    """Generate a professional PDF report with logo and branding."""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define custom styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#764ba2'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # Header style
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Info box style
    info_style = ParagraphStyle(
        'InfoBox',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=6,
        leftIndent=20,
        fontName='Helvetica'
    )
    
    # Add PixelMed Logo Header
    elements.append(Paragraph("PixelMed", title_style))
    elements.append(Paragraph("AI-Powered Medical Image Analysis", subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add a horizontal line
    line_data = [['', '']]
    line_table = Table(line_data, colWidths=[6*inch])
    line_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 2, colors.HexColor('#667eea')),
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Add report metadata
    current_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    metadata_text = f"""
    <b>Report Generated:</b> {current_date}<br/>
    <b>Image File:</b> {filename}<br/>
    <b>Analysis Model:</b> Google Gemini 2.0 Flash
    """
    elements.append(Paragraph(metadata_text, info_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Add medical image if exists
    if os.path.exists(image_path):
        try:
            img = RLImage(image_path, width=4*inch, height=3*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.2*inch))
        except:
            pass
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Parse and add report content
    lines = report_text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            elements.append(Spacer(1, 0.1*inch))
            continue
        
        # Handle headers (###, ##, #)
        if line.startswith('###'):
            header_text = line.replace('###', '').strip()
            elements.append(Paragraph(header_text, header_style))
        elif line.startswith('##'):
            header_text = line.replace('##', '').strip()
            elements.append(Paragraph(header_text, header_style))
        elif line.startswith('#'):
            header_text = line.replace('#', '').strip()
            elements.append(Paragraph(header_text, header_style))
        
        # Handle bullet points
        elif line.startswith('-') or line.startswith('•'):
            bullet_text = line[1:].strip()
            bullet_text = f"• {bullet_text}"
            elements.append(Paragraph(bullet_text, body_style))
        
        # Handle numbered lists
        elif re.match(r'^\d+\.', line):
            elements.append(Paragraph(line, body_style))
        
        # Regular paragraph
        else:
            # Make bold text work
            line = line.replace('**', '<b>').replace('**', '</b>')
            elements.append(Paragraph(line, body_style))
    
    # Add footer disclaimer
    elements.append(Spacer(1, 0.3*inch))
    line_table2 = Table([['', '']], colWidths=[6*inch])
    line_table2.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 1, colors.grey),
    ]))
    elements.append(line_table2)
    
    disclaimer = """
    <b>Medical Disclaimer:</b> This report is generated by AI for educational and informational 
    purposes only. It should not be used for clinical diagnosis or treatment decisions. 
    Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment.
    """
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(disclaimer, disclaimer_style))
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer


# ------------------------------------
# MEDICAL ANALYSIS FUNCTION
# ------------------------------------
def analyze_medical_image(image_path):
    """Uses Gemini 2.0 Flash to analyze a medical image + perform research search."""

    try:
        with open(image_path, "rb") as img:
            image_bytes = img.read()

        final_prompt = """
You are a highly skilled medical imaging expert. Analyze the medical image and give structured output:

### 1. Image Type & Region
- Identify imaging modality (X-ray/MRI/CT/Ultrasound/etc)
- Anatomical region + positioning
- Evaluate image quality and technical adequacy

### 2. Key Findings
- Primary observations
- Possible abnormalities
- Approximated measurements (if inferable)
- Pattern analysis

### 3. Diagnostic Assessment
- Primary diagnosis + confidence %
- Differential diagnoses (ranked)
- Evidence-based justification
- Urgent / critical alerts

### 4. Patient-Friendly Explanation
- Explain findings in simple, clear language
- Use analogies when possible

### 5. Research Context
- Summarize 2–3 modern research insights
- Provide latest standard treatment options
- Provide risk factors and prevention

IMPORTANT:
- Use clean markdown formatting.
- Do NOT hallucinate facts not inferable from the image.
"""

        response = model.generate_content(
            [
                {"mime_type": "image/jpeg", "data": image_bytes},
                final_prompt
            ]
        )

        return response.text

    except Exception as e:
        return f"⚠️ Error analyzing image: {str(e)}"


# ------------------------------------
# STREAMLIT UI SETUP
# ------------------------------------
st.set_page_config(
    page_title="PixelMed - AI Medical Image Analysis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with medical theme - UPDATED WITH TEXT VISIBILITY FIX
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Main Background with Medical Theme */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    .stApp {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    }
    
    /* Custom Container */
    .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        margin-top: 2rem;
        backdrop-filter: blur(10px);
    }
    
    /* Header Styling */
    h1, h2, h3 {
        font-family: 'Poppins', sans-serif;
        color: #2d3748;
    }
    
    p, div, span {
        font-family: 'Inter', sans-serif;
    }
    
    /* Logo and Title Container */
    .logo-container {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
    }
    
    .logo-svg {
        width: 120px;
        height: 120px;
        margin: 0 auto 1rem;
        filter: drop-shadow(0 5px 15px rgba(255, 255, 255, 0.3));
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: 2px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .subtitle {
        color: #e0e7ff;
        font-size: 1.2rem;
        font-weight: 300;
        margin-top: 0.5rem;
        letter-spacing: 1px;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        font-family: 'Poppins', sans-serif;
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Download Button */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 8px 20px rgba(72, 187, 120, 0.4);
    }
    
    .stDownloadButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(72, 187, 120, 0.6);
    }
    
    /* Cards */
    .feature-card {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border: 2px solid #667eea;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #718096;
        font-size: 0.95rem;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #ebf4ff 0%, #dbeafe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    
    .info-box h3 {
        color: #1e3a8a !important;
        font-weight: 600;
    }
    
    .info-box p {
        color: #1e40af !important;
        font-weight: 400;
    }
    
    /* Warning Box */
    .warning-box {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #f56565;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(245, 101, 101, 0.2);
    }
    
    .warning-box p {
        color: #991b1b !important;
        font-weight: 500;
    }
    
    .warning-box strong {
        color: #7f1d1d !important;
    }
    
    /* Sidebar Styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .css-1d391kg .sidebar-content {
        background: transparent;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: white;
        font-weight: 500;
    }
    
    /* Image Container */
    .image-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        border: 3px solid #667eea;
    }
    
    /* Success Message */
    .success-box {
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #48bb78;
        margin: 1.5rem 0;
        box-shadow: 0 4px 12px rgba(72, 187, 120, 0.2);
    }
    
    /* Report Container - FIXED TEXT VISIBILITY */
    .report-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
        border: 2px solid #667eea;
    }
    
    /* Force all text to be visible in report container */
    .report-container * {
        color: #2d3748 !important;
    }
    
    .report-container h1,
    .report-container h2,
    .report-container h3,
    .report-container h4 {
        color: #667eea !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    .report-container p,
    .report-container li,
    .report-container span {
        color: #1a202c !important;
        line-height: 1.8 !important;
        font-size: 1rem !important;
    }
    
    .report-container strong {
        color: #667eea !important;
        font-weight: 600 !important;
    }
    
    .report-container ul, 
    .report-container ol {
        padding-left: 1.5rem !important;
        margin: 1rem 0 !important;
    }
    
    .report-container code {
        background: #f7fafc !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
        color: #e53e3e !important;
        font-family: 'Courier New', monospace !important;
    }
    
    /* Markdown content styling */
    .stMarkdown {
        color: #1a202c !important;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Header with Logo
st.markdown("""
    <div class="logo-container">
        <svg class="logo-svg" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
            <circle cx="100" cy="100" r="95" fill="rgba(255, 255, 255, 0.2)" stroke="white" stroke-width="3"/>
            <rect x="85" y="50" width="30" height="100" fill="white" rx="5"/>
            <rect x="50" y="85" width="100" height="30" fill="white" rx="5"/>
            <rect x="70" y="70" width="15" height="15" fill="#48bb78" opacity="0.8"/>
            <rect x="115" y="70" width="15" height="15" fill="#4299e1" opacity="0.8"/>
            <rect x="70" y="115" width="15" height="15" fill="#ed64a6" opacity="0.8"/>
            <rect x="115" y="115" width="15" height="15" fill="#f6ad55" opacity="0.8"/>
            <polyline points="30,100 50,100 60,80 70,120 80,100 200,100" 
                      stroke="white" stroke-width="3" fill="none" opacity="0.6"/>
        </svg>
        <h1 class="main-title">PixelMed</h1>
        <p class="subtitle">AI-Powered Medical Image Analysis</p>
    </div>
    """, unsafe_allow_html=True)

# Description
st.markdown("""
    <div class="info-box">
        <h3 style="margin-top: 0;">🔬 Welcome to PixelMed</h3>
        <p>Upload a medical image (X-ray, MRI, CT, Ultrasound, Skin Image, etc.) and get an AI-generated 
        medical-grade analysis with research-backed insights powered by Google Gemini 2.0 Flash.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class="warning-box">
        <p style="margin: 0;"><strong>⚠️ Medical Disclaimer:</strong> This tool is for educational and informational purposes only. 
        Not for clinical diagnosis. Always consult a qualified healthcare professional for medical advice.</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("<h2 style='color: white; text-align: center;'>📤 Upload Image</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border-color: rgba(255,255,255,0.3);'>", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader(
    "Choose a medical image",
    type=["jpg", "jpeg", "png", "bmp", "gif"],
    help="Upload X-ray, MRI, CT scan, or other medical images"
)

# ------------------------------------
# MAIN UI LOGIC
# ------------------------------------
if uploaded_file:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("<h2 style='color: #667eea;'>📸 Uploaded Image</h2>", unsafe_allow_html=True)
        st.markdown("<div class='image-container'>", unsafe_allow_html=True)
        st.image(uploaded_file, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<h2 style='color: #667eea;'>📋 Image Information</h2>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class="feature-card">
                <div style="text-align: left;">
                    <p><strong>📁 Filename:</strong> {uploaded_file.name}</p>
                    <p><strong>🖼️ File Type:</strong> {uploaded_file.type}</p>
                    <p><strong>💾 File Size:</strong> {uploaded_file.size / 1024:.2f} KB</p>
                    <p><strong>📅 Upload Status:</strong> <span style="color: #48bb78;">✓ Ready</span></p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.sidebar.button("🔍 Analyze Image", type="primary"):
        with st.spinner("🔄 Analyzing the image... Please wait"):
            ext = uploaded_file.type.split("/")[-1]
            image_path = f"temp_image.{ext}"

            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            report = analyze_medical_image(image_path)

            st.markdown("""
                <div class="success-box">
                    <h3 style="margin: 0; color: #48bb78;">✅ Analysis Complete!</h3>
                </div>
                """, unsafe_allow_html=True)
            
            # Display report with proper text visibility
            st.markdown("<div class='report-container'>", unsafe_allow_html=True)
            st.markdown("<h2 style='color: #667eea;'>📋 Detailed Analysis Report</h2>", unsafe_allow_html=True)
            st.markdown(report, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Download buttons in columns
            col_btn1, col_btn2 = st.columns(2, gap="medium")
            
            with col_btn1:
                st.download_button(
                    label="📥 Download as Markdown",
                    data=report,
                    file_name=f"pixelmed_analysis_{uploaded_file.name}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            with col_btn2:
                # Generate PDF
                pdf_buffer = create_pdf_report(report, image_path, uploaded_file.name)
                st.download_button(
                    label="📄 Download as PDF",
                    data=pdf_buffer,
                    file_name=f"pixelmed_analysis_{uploaded_file.name}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            os.remove(image_path)

else:
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h2 style="color: #667eea;">⬅️ Upload a medical image to begin analysis</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center; color: #2d3748; margin: 3rem 0 2rem 0;'>🏥 What Can PixelMed Analyze?</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🦴</div>
                <div class="feature-title">X-rays</div>
                <div class="feature-desc">Fractures, chest X-rays, dental scans, bone density analysis</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <div class="feature-title">MRI Scans</div>
                <div class="feature-desc">Brain imaging, spine analysis, joint examinations</div>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🫁</div>
                <div class="feature-title">CT Scans</div>
                <div class="feature-desc">Head, chest, abdomen, detailed cross-sections</div>
            </div>
            """, unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3, gap="large")

    with col4:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">👶</div>
                <div class="feature-title">Ultrasound</div>
                <div class="feature-desc">Prenatal imaging, organ examination, soft tissue analysis</div>
            </div>
            """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🔬</div>
                <div class="feature-title">Pathology</div>
                <div class="feature-desc">Tissue samples, microscopy, cellular analysis</div>
            </div>
            """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🩺</div>
                <div class="feature-title">Dermatology</div>
                <div class="feature-desc">Skin conditions, lesions, dermatoscopy images</div>
            </div>
            """, unsafe_allow_html=True)

# Sidebar Footer
st.sidebar.markdown("<hr style='border-color: rgba(255,255,255,0.3); margin: 3rem 0 1rem 0;'>", unsafe_allow_html=True)
st.sidebar.markdown("""
    <div style='text-align: center; color: white;'>
        <p style='font-size: 0.9rem; margin: 0.5rem 0;'>🤖 Powered by</p>
        <p style='font-size: 1.1rem; font-weight: 600; margin: 0.5rem 0;'>Google Gemini 2.0 Flash</p>
        <p style='font-size: 0.85rem; opacity: 0.8; margin: 1rem 0 0 0;'>Version 2.0.0</p>
    </div>
    """, unsafe_allow_html=True)
