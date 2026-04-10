import streamlit as st
import google.generativeai as genai
import tempfile
import os
import whisper

# --- 1. Page Config ---
st.set_page_config(page_title="Strategic Auditor 2026", layout="wide")

# Load Whisper (Free & Local)
@st.cache_resource
def load_whisper():
    # 'base' is fast. Change to 'small' for better Arabic if needed.
    return whisper.load_model("base") 

whisper_model = load_whisper()

# --- 2. State Management ---
if 'transcript' not in st.session_state: st.session_state.transcript = ""
if 'analysis' not in st.session_state: st.session_state.analysis = ""
if 'last_uploaded_file' not in st.session_state: st.session_state.last_uploaded_file = None

st.title("🎙️ AI Strategic Call Auditor")

# --- 3. Sidebar (API Key Input) ---
with st.sidebar:
    st.header("⚙️ Configuration")
    user_api_key = st.text_input("Enter Gemini API Key", type="password", help="Get your key from https://aistudio.google.com/app/apikey")
    st.markdown("---")
    st.info("Whisper is transcribing locally (FREE). Gemini is for Analysis.")

# --- 4. Logic Functions ---
def analyze_with_gemini(transcript, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-1.5-flash') 
    prompt = f"""
    Audit this call based on the PILLARS: Motivation, Price, Timeline, Condition, Rapport.
    Use the CARE Model for objections.
    
    Transcript: {transcript}
    """
    res = model.generate_content(prompt)
    return res.text

# --- 5. Main UI ---
uploaded_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3', 'm4a'])

# 🚩 RESET LOGIC: Law rafa3na file gadeed, n-faddy el-qadeem
if uploaded_file:
    if st.session_state.last_uploaded_file != uploaded_file.name:
        st.session_state.transcript = ""
        st.session_state.analysis = ""
        st.session_state.last_uploaded_file = uploaded_file.name
        st.rerun()

    # STEP 1: Transcription
    if st.button("Step 1: Extract Transcript 📄"):
        with st.spinner("Whisper is transcribing locally... Please wait."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                # Run Whisper
                result = whisper_model.transcribe(tmp_path)
                st.session_state.transcript = result['text']
                os.remove(tmp_path)
                st.success("✅ Transcription Done!")
            except Exception as e:
                st.error(f"Transcription Error: {e}")

    # Show Transcript
    if st.session_state.transcript:
        st.markdown("### 📄 Transcript")
        st.text_area("", st.session_state.transcript, height=250)

        # STEP 2: Analysis
        if st.button("Step 2: Run Strategic Analysis 🚀"):
            if not user_api_key:
                st.error("❌ Please enter your Gemini API Key in the sidebar!")
            else:
                with st.spinner("Analyzing with Gemini..."):
                    try:
                        analysis = analyze_with_gemini(st.session_state.transcript, user_api_key)
                        st.session_state.analysis = analysis
                        st.success("✅ Analysis Complete!")
                    except Exception as e:
                        st.error(f"Analysis Error: {e}")

    # Display Analysis
    if st.session_state.analysis:
        st.markdown("---")
        st.markdown("### 📊 Strategic Analysis Report")
        st.markdown(st.session_state.analysis)
        st.download_button("Download Report", st.session_state.analysis, file_name="audit_report.md")
