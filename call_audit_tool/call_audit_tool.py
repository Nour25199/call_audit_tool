import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- Page Configuration ---
st.set_page_config(page_title="Strategic Call Auditor Pro", layout="wide", page_icon="🎯")

# --- Session State Management (to prevent old reports from showing) ---
if 'last_uploaded_file' not in st.session_state:
    st.session_state.last_uploaded_file = None
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'analysis' not in st.session_state:
    st.session_state.analysis = ""

st.title("🎙️ AI Strategic Call Auditor & Sales Coach")
st.markdown("Fully English Detailed Analysis | Based on Lead Manager Training Material")

# --- Sidebar for Security ---
with st.sidebar:
    st.header("⚙️ Settings")
    gemini_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get your key: https://aistudio.google.com/app/apikey")
    st.divider()
    st.caption("This tool is strictly programmed for English-only detailed auditing.")

# --- Training Material Reference ---
TRAINING_MATERIAL = """
PILLARS: Motivation, Price, Timeline, Condition, Rapport.
MODELS: CARE (Clarify, Acknowledge, Reframe, Explore).
QUALIFICATION: Hot (2+ criteria), Warm, Long-term.
CREDIBILITY: Local family-owned, A+ BBB, buy as-is, no fees.
"""

uploaded_file = st.file_uploader("Upload Audio (wav, mp3) or Text (.txt)", type=['txt', 'wav', 'mp3', 'm4a'])

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
            if 'flash' in m_name.lower(): return m_name
        return available_models[0] if available_models else None
    except: return None

if uploaded_file and gemini_key:
    model_name = find_best_model(gemini_key)
    if model_name:
        model = genai.GenerativeModel(model_name)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Step 1: Extract Transcript 📄"):
                try:
                    with st.spinner("Transcribing..."):
                        if uploaded_file.type.startswith('audio/'):
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
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
                    st.error(f"Error in Step 1: {str(e)}")

        if st.session_state.transcript:
            st.subheader("📄 The Transcript")
            st.text_area("Content:", st.session_state.transcript, height=200)
            
            st.divider()

            if st.button("Step 2: Run Strategic Analysis 🚀"):
                try:
                    with st.spinner("Analyzing call against training..."):
                        # STRICT PROMPT FOR ENGLISH AND DETAILED STRUCTURE
                        strategic_prompt = f"""
                        You are a Senior Real Estate Sales Auditor. 
                        LANGUAGE: You MUST respond in 100% ENGLISH. No Arabic characters.
                        TASK: Perform a deep-dive audit of the transcript based on the Training Material.

                        TRAINING MATERIAL:
                        {TRAINING_MATERIAL}

                        REQUIRED FORMAT (Follow this EXACTLY, one key per line):

                        This audit is based on your lead manager training materials, focusing on the Five Pillars, the CARE Model for objections, and Building Credibility guidelines.

                        ### **Notes**
                        **Call Summary:** (Detailed paragraph summary)
                        **Situation:** (Seller context)
                        **Motivation / Pain:** (Deep dive into why they sell)
                        **Timeline:** (Urgency level)
                        **Condition (high-level):** (Property details)
                        **Price Expectation + Reason:** (Numbers and reasons)
                        **Decision Maker(s):** (Who is involved)
                        **Objections / Concerns:** (What concerns were raised)
                        **Outcome / Next Step:** (Plan agreed upon)
                        **Important Notes:** (Legal/Trust issues, etc.)

                        ---
                        ### **Strengths**
                        (List detailed strengths using specific Pillars or models from the training)

                        ---
                        ### **Areas to Improve (Detailed)**
                        (Identify specific failures in applying CARE, Credibility, or Mirroring. Explain WHY it failed)

                        ---
                        ### **Missed Opportunity (Detailed)**
                        (Identify specific pivots or questions skipped from the manual)

                        ---
                        ### **Coach Tip (Exact sentence/question to use next time)**
                        (Provide the exact script based on the training material)

                        Transcript:
                        {st.session_state.transcript}
                        """
                        
                        analysis_response = model.generate_content(strategic_prompt)
                        st.session_state.analysis = analysis_response.text
                        st.success("✅ Analysis Complete!")
                except Exception as e:
                    st.error(f"Error in Step 2: {str(e)}")

        if st.session_state.analysis:
            st.subheader("🧠 Strategic Audit Report")
            st.markdown(st.session_state.analysis)
            st.download_button("Download Audit Report (.md)", st.session_state.analysis, file_name=f"Audit_{uploaded_file.name}.md")
