import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# ------------------------------------
# CONFIGURE GOOGLE API
# AIzaSyCb-lkObsyDqVUPW78vwLSnHX6M0AvCFzc
# ------------------------------------
GOOGLE_API_KEY = "AIzaSyCb-lkObsyDqVUPW78vwLSnHX6M0AvCFzc"
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")


# ------------------------------------
# MEDICAL ANALYSIS FUNCTION
# ------------------------------------
def analyze_medical_image(image_path):
    """Uses Gemini 2.0 Flash to analyze a medical image + perform research search."""

    try:
        # Read image as bytes
        with open(image_path, "rb") as img:
            image_bytes = img.read()

        # Prompt for analysis
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

        # Send image + prompt
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
st.set_page_config(page_title="PixelMed", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🩺 PixelMed 🔬")

st.markdown("""
Upload a medical image (X-ray, MRI, CT, Ultrasound, Skin Image, etc.)  
and get an AI-generated medical-grade analysis + research-backed insights.

⚠️ *Not for clinical use. Always consult a doctor.*  
""")

# Sidebar
st.sidebar.header("Upload Your Medical Image:")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "Choose image",
    type=["jpg", "jpeg", "png", "bmp", "gif"]
)

# ------------------------------------
# MAIN UI LOGIC
# ------------------------------------
if uploaded_file:

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📸 Uploaded Image")
        st.image(uploaded_file, caption="Uploaded Medical Image", use_column_width=True)

    with col2:
        st.subheader("📋 Image Information")
        st.write(f"**Filename:** {uploaded_file.name}")
        st.write(f"**File type:** {uploaded_file.type}")
        st.write(f"**File size:** {uploaded_file.size / 1024:.2f} KB")

    st.markdown("---")

    if st.sidebar.button("🔍 Analyze Image", type="primary"):
        with st.spinner("Analyzing the image... Please wait ⏳"):

            ext = uploaded_file.type.split("/")[-1]
            image_path = f"temp_image.{ext}"

            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Run analysis
            report = analyze_medical_image(image_path)

            # Display results
            st.success("✅ Analysis Complete!")
            st.subheader("📋 Detailed Analysis Report")
            st.markdown(report, unsafe_allow_html=True)

            # Download option
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"medical_analysis_{uploaded_file.name}.md",
                mime="text/markdown"
            )

            # Cleanup
            os.remove(image_path)

else:
    st.info("⬅️ Upload a medical image from the sidebar to begin.")

    st.markdown("### 📚 What This Tool Can Analyze:")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🦴 X-rays**")
        st.caption("Fractures, chest X-rays, dental scans")

    with col2:
        st.markdown("**🧠 MRI**")
        st.caption("Brain, spine, joints")

    with col3:
        st.markdown("**🫁 CT Scans**")
        st.caption("Head, chest, abdomen")

st.sidebar.markdown("---")
st.sidebar.caption("Powered by Google Gemini 2.0 Flash 🤖")
st.sidebar.caption("Version 2.0.0")
