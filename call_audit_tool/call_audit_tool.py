import streamlit as st
import google.generativeai as genai
import tempfile
import os
import whisper

# --- 1. Page Config ---
st.set_page_config(page_title="Strategic Auditor 2026", layout="wide")

# Load Whisper (Tiny model for stability on Free Servers)
@st.cache_resource
def load_whisper():
    # 'tiny' is the smallest and most stable for 1GB RAM limits
    return whisper.load_model("tiny") 

whisper_model = load_whisper()

# --- 2. State Management ---
if 'transcript' not in st.session_state: st.session_state.transcript = ""
if 'analysis' not in st.session_state: st.session_state.analysis = ""
if 'last_uploaded_file' not in st.session_state: st.session_state.last_uploaded_file = None

st.title("🎙️ AI Strategic Call Auditor")

# --- 3. Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuration")
    user_api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Mode: Ultra-Light (Whisper Tiny + Gemini Flash)")

# --- 4. Logic Functions ---
def analyze_with_gemini(transcript, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-1.5-flash') 
    prompt = f"Audit this call based on PILLARS: Motivation, Price, Timeline, Condition, Rapport. Transcript: {transcript}"
    res = model.generate_content(prompt)
    return res.text

# --- 5. Main UI ---
uploaded_file = st.file_uploader("Upload Audio", type=['wav', 'mp3', 'm4a'])

if uploaded_file:
    # Reset logic if new file is uploaded
    if st.session_state.last_uploaded_file != uploaded_file.name:
        st.session_state.transcript = ""
        st.session_state.analysis = ""
        st.session_state.last_uploaded_file = uploaded_file.name
        st.rerun()

    # STEP 1: Transcription
    if st.button("Step 1: Extract Transcript 📄"):
        with st.spinner("Transcribing... (Using Tiny Model for Speed)"):
            try:
                # Save to temp file
                suffix = f".{uploaded_file.name.split('.')[-1]}"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                # Direct transcribe using the path (most RAM efficient)
                result = whisper_model.transcribe(tmp_path, fp16=False)
                st.session_state.transcript = result['text']
                
                os.remove(tmp_path)
                st.success("✅ Done!")
            except Exception as e:
                st.error(f"Error: {e}")

    # Display Transcript
    if st.session_state.transcript:
        st.text_area("Transcript:", st.session_state.transcript, height=200)

        # STEP 2: Analysis
        if st.button("Step 2: Run Strategic Analysis 🚀"):
            if user_api_key:
                with st.spinner("Analyzing..."):
                    try:
                        analysis = analyze_with_gemini(st.session_state.transcript, user_api_key)
                        st.session_state.analysis = analysis
                        st.success("✅ Analysis Complete!")
                    except Exception as e:
                        st.error(f"Analysis Error: {e}")
            else:
                st.warning("Please enter API Key")

    # Display Results
    if st.session_state.analysis:
        st.markdown(st.session_state.analysis)
        st.download_button("Download Report", st.session_state.analysis, file_name="audit.md")
