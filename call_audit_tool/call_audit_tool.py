import streamlit as st
import google.generativeai as genai
import tempfile
import os

st.set_page_config(page_title="Strategic Call Auditor", layout="wide", page_icon="🎯")

st.title("🎙️ AI Strategic Call Auditor")
st.markdown("تحليل المكالمات بناءً على الـ Structure والـ Training Module الخاص بك")

# --- الماتريال (Reference Material) ---
TRAINING_MATERIAL = """
[The Five Pillars: Motivation, Price, Timeline, Condition, Rapport]
[Call Next Actions & Qualification: Hot, Warm, Long-term]
[Objection Handling: CARE Model]
[Credibility: As-is, No fees, Flexible closing]
[Deep Motivation questions & Rapport building techniques]
"""

with st.sidebar:
    st.header("⚙️ Settings")
    gemini_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get your key: https://aistudio.google.com/app/apikey")

if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'analysis' not in st.session_state:
    st.session_state.analysis = ""

uploaded_file = st.file_uploader("Upload Audio or Text", type=['txt', 'wav', 'mp3', 'm4a'])

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
                            response = model.generate_content(["Provide a word-for-word transcript. No summary.", audio_file])
                            st.session_state.transcript = response.text
                            os.remove(tmp_path)
                        else:
                            st.session_state.transcript = uploaded_file.read().decode("utf-8")
                        st.success("✅ Transcript Extracted!")
                except Exception as e:
                    st.error(f"Error in Step 1: {str(e)}")

        if st.session_state.transcript:
            st.subheader("📄 The Transcript")
            st.text_area("Original Content:", st.session_state.transcript, height=200)
            
            st.divider()

            if st.button("Step 2: Run Strategic Analysis 🚀"):
                try:
                    with st.spinner("Auditing against Training Module..."):
                        # الـ Prompt الجديد الملتزم بالـ Structure المطلوب حرفياً
                        strategic_prompt = f"""
                        You are an expert Real Estate Sales Auditor. 
                        Use the provided Training Material to judge the agent's performance.

                        STRICT REPORT STRUCTURE (Follow this EXACTLY):

                        ### **Notes**
                        **Call summary:** (Brief overview)
                        **Situation:** (Seller's current context)
                        **Motivation / Pain:** (Why they want to sell)
                        **Timeline:** (Urgency level)
                        **Condition (high-level):** (Property status)
                        **Price Expectation + reason:** (Asking price and why they chose it)
                        **Decision Maker(s):** (Who else is involved?)
                        **Objections / Concerns:** (What held them back?)
                        **Outcome / Next Step:** (What was agreed upon?)
                        **Important Notes:** (Tenants, liens, probate, etc.)

                        ---
                        **Strength:**
                        - (What did the agent do well based on the training?)

                        **Areas to Improve:**
                        - (What was weak?)

                        **Missed Opportunity:**
                        - (What specific pillar or question did they skip?)

                        **Coach Tip:**
                        - (Provide an EXACT sentence or question the agent should use next time based on the script/training.)

                        STRICT RULES:
                        1. NO section numbers (Do not mention "Section 1" etc.).
                        2. 100% coverage of the transcript.
                        3. Use ONLY the provided Training Material to judge the "Missed Opportunities" and "Coach Tips".

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
            st.download_button("Download Report (.md)", st.session_state.analysis, file_name="Audit_Report.md")
