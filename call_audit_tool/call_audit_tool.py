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
    return whisper.load_model("base") # "base" is fast, use "small" for better Arabic

whisper_model = load_whisper()

# --- 2. State Management ---
if 'transcript' not in st.session_state: st.session_state.transcript = ""
if 'analysis' not in st.session_state: st.session_state.analysis = ""

st.title("🎙️ AI Strategic Call Auditor")

# --- 3. Sidebar (Hena Ben-ask 3ala el-Key) ---
with st.sidebar:
    st.header("⚙️ Configuration")
    # El-input da "Password" type ya3ny msh hayban we mesh hayetsayiv fey el-code
    user_api_key = st.text_input("Enter Gemini API Key", type="password", help="Get your key from https://aistudio.google.com/app/apikey")
    
    st.markdown("---")
    st.info("Whisper is running locally for FREE transcription.")

# --- 4. Logic Functions ---
def analyze_with_gemini(transcript, key):
    genai.configure(api_key=key)
    # 1.5-flash ashan ykoun fey el-Free Quota (1500 RPM)
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

if uploaded_file:
    # STEP 1: Transcription
    if st.button("Step 1: Extract Transcript 📄"):
        with st.spinner("Whisper is transcribing locally (No API used)..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            # Run Whisper Locally
            result = whisper_model.transcribe(tmp_path)
            st.session_state.transcript = result['text']
            os.remove(tmp_path)
            st.success("✅ Transcription Done!")

    # Show Transcript if exists
    if st.session_state.transcript:
        st.text_area("Transcript:", st.session_state.transcript, height=200)

        # STEP 2: Analysis (Hena ben-check law m3ana Key)
        if st.button("Step 2: Run Strategic Analysis 🚀"):
            if not user_api_key:
                st.error("❌ Please enter your Gemini API Key in the sidebar first!")
            else:
                with st.spinner("Analyzing with Gemini..."):
                    try:
                        analysis = analyze_with_gemini(st.session_state.transcript, user_api_key)
                        st.session_state.analysis = analysis
                        st.success("✅ Audit Complete!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # Display Analysis Result
    if st.session_state.analysis:
        st.markdown("### 📊 Strategic Analysis Report")
        st.markdown(st.session_state.analysis)
        st.download_button("Download Report", st.session_state.analysis, file_name="audit_report.md")
