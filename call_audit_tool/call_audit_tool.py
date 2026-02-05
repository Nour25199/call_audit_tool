import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- Page Configuration ---
st.set_page_config(page_title="Strategic Call Auditor Pro", layout="wide", page_icon="🎯")

# --- Session State Management ---
if 'last_uploaded_file' not in st.session_state:
    st.session_state.last_uploaded_file = None
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'analysis' not in st.session_state:
    st.session_state.analysis = ""

st.title("🎙️ AI Strategic Call Auditor & Sales Coach")
st.markdown("Fully English Detailed Analysis | Based on Lead Manager Training Material")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    gemini_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get your key: https://aistudio.google.com/app/apikey")
    st.divider()
    st.caption("Powered by Gemini 1.5 Flash for high-volume auditing.")

# --- Training Material Reference (The Knowledge Base) ---
TRAINING_MATERIAL = """
PILLARS: Motivation (Why), Price (Uncover expectations), Timeline (Urgency), Condition (Repairs/Age), Rapport (Trust/Mirroring).
MODELS: CARE (Clarify, Acknowledge, Reframe, Explore).
QUALIFICATION: Hot (Motivation + Price/Timeline < 30 days), Warm, Long-term.
CREDIBILITY: Local family-owned, 6+ years experience, A+ BBB, buy as-is, no fees, flexible closing.
OBJECTION EXAMPLES: "Price too low", "Not in a rush", "Need to find a place first".
"""

# --- File Uploader ---
uploaded_file = st.file_uploader("Upload Audio (wav, mp3) or Text (.txt)", type=['txt', 'wav', 'mp3', 'm4a'])

# Reset logic: Clear old analysis if a new file is uploaded
if uploaded_file is not None:
    if uploaded_file.name != st.session_state.last_uploaded_file:
        st.session_state.transcript = ""
        st.session_state.analysis = ""
        st.session_state.last_uploaded_file = uploaded_file.name

# --- Model Discovery Function (Fixed & Prioritizing 1.5 Flash) ---
def find_best_model(api_key):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Priority 1: Gemini 1.5 Flash (High Quota)
        for m_name in available_models:
            if '1.5-flash' in m_name.lower(): 
                return m_name
        # Priority 2: Any other Flash model
        for m_name in available_models:
            if 'flash' in m_name.lower(): 
                return m_name
        return available_models[0] if available_models else None
    except:
        return None

# --- Main App Logic ---
if uploaded_file and gemini_key:
    model_name = find_best_model(gemini_key)
    if model_name:
        model = genai.GenerativeModel(model_name)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Step 1: Extract Transcript 📄"):
                try:
                    with st.spinner("Processing file..."):
                        if uploaded_file.type.startswith('audio/'):
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_path = tmp_file.name
                            audio_file = genai.upload_file(path=tmp_path)
                            response = model.generate_content(["Provide a word-for-word transcript in English. Do not summarize.", audio_file])
                            st.session_state.transcript = response.text
                            os.remove(tmp_path)
                        else:
                            st.session_state.transcript = uploaded_file.read().decode("utf-8")
                        st.success("✅ Transcript Ready!")
                except Exception as e:
                    st.error(f"Step 1 Error: {str(e)}")

        if st.session_state.transcript:
            st.subheader("📄 The Transcript")
            st.text_area("Original Content:", st.session_state.transcript, height=200)
            
            st.divider()

            if st.button("Step 2: Run Strategic Analysis 🚀"):
                try:
                    with
