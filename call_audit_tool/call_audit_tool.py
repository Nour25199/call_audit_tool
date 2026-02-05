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

# --- Training Material Reference ---
TRAINING_MATERIAL = """
PILLARS: Motivation, Price, Timeline, Condition, Rapport.
MODELS: CARE (Clarify, Acknowledge, Reframe, Explore).
QUALIFICATION: Hot (2+ criteria), Warm, Long-term.
CREDIBILITY: Local family-owned, A+ BBB, buy as-is, no fees, flexible closing.
"""

uploaded_file = st.file_uploader("Upload Audio or Text", type=['txt', 'wav', 'mp3', 'm4a'])

# Reset logic when a new file is uploaded
if uploaded_file is not None:
    if uploaded_file.name != st.session_state.last_uploaded_file:
        st.session_state.transcript = ""
        st.session_state.analysis = ""
        st.session_state.last_uploaded_file = uploaded_file.name

def find_best_model(api_key):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m_name in available_models:
            if '1.5-flash' in m_name.lower(): 
                return m_name
        return available_models[0] if available_models else None
    except:
        return None

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
                            # تقصير السطر ده عشان ميعملش Syntax Error
                            suffix = f".{uploaded_file.name.split('.')[-1]}"
                            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_path = tmp_file.name
                            
                            audio_file = genai.upload_file(path=tmp_path)
                            response = model.generate_content(["Provide a word-for-word transcript in English. No analysis.", audio_file])
                            st.session_state.transcript = response.text
                            os.remove(tmp_path)
                        else:
                            st.session_state.transcript = uploaded_file.read().decode("utf-8")
                        st.success("✅ Transcript Ready!")
                except Exception as e:
                    st.error(f"Step 1 Error: {str(e)}")

        if st.session_state.transcript:
            st.subheader("📄 The Transcript")
            st.text_area("Content:", st.session_state.transcript, height=200)
            
            st.divider()

            if st.button("Step 2: Run Strategic Analysis 🚀"):
                try:
                    with st.spinner("Auditing..."):
                        strategic_prompt = f"""
                        You are a Senior Real Estate Sales Auditor. 
                        LANGUAGE: Respond in 100% ENGLISH. No Arabic.
                        TASK: Audit the transcript based on the Training Material.

                        TRAINING MATERIAL:
                        {TRAINING_MATERIAL}

                        REPORT STRUCTURE:
                        ### **Notes**
                        **Call summary:** (Provide a detailed paragraph summary)
                        **Situation:** (Seller context)
                        **Motivation / Pain:** (Why they sell)
                        **Timeline:** (Urgency level)
                        **Condition (high-level):** (Property details)
                        **Price Expectation + reason:** (Price logic)
                        **Decision Maker(s):** (Who is involved)
                        **Objections / Concerns:** (Concerns raised)
                        **Outcome / Next Step:** (Plan agreed)
                        **Important Notes:** (Red flags)

                        ---
                        ### **Strengths**
                        - (Detailed strengths based on training)
                        ---
                        ### **Areas to Improve (Detailed)**
                        - (Analyze failures in CARE or Pillars)
                        ---
                        ### **Missed Opportunity (Detailed)**
                        - (Specific pivots skipped)
                        ---
                        ### **Coach Tip (Exact sentence/question to use next time)**
                        - (Exact script based on material)

                        Transcript:
                        {st.session_state.transcript}
                        """
                        analysis_response = model.generate_content(strategic_prompt)
                        st.session_state.analysis = analysis_response.text
                        st.success("✅ Analysis Complete!")

    if st.session_state.analysis:
        st.subheader("🧠 Strategic Audit Report")
        st.markdown(st.session_state.analysis)
        st.download_button("Download Report (.md)", st.session_state.analysis, file_name=f"Audit_{uploaded_file.name}.md")
