import streamlit as st
import google.generativeai as genai
import tempfile
import os

# 1. Page Config
st.set_page_config(page_title="Strategic Auditor", layout="wide")

# 2. Session States
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'analysis' not in st.session_state:
    st.session_state.analysis = ""
if 'last_file' not in st.session_state:
    st.session_state.last_file = None

st.title("🎙️ AI Strategic Call Auditor")

# 3. Sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get key: https://aistudio.google.com/app/apikey")

# 4. Training Material
MATERIAL = """
PILLARS: Motivation, Price, Timeline, Condition, Rapport.
MODELS: CARE (Clarify, Acknowledge, Reframe, Explore).
QUALIFICATION: Hot (2+ criteria), Warm, Long-term.
CREDIBILITY: Local family-owned, A+ BBB, buy as-is, no fees.
"""

# 5. File Uploader
uploaded_file = st.file_uploader("Upload File", type=['txt', 'wav', 'mp3', 'm4a'])

# Reset if new file
if uploaded_file and uploaded_file.name != st.session_state.last_file:
    st.session_state.transcript = ""
    st.session_state.analysis = ""
    st.session_state.last_file = uploaded_file.name

# 6. Model Discovery
def get_model(key):
    try:
        genai.configure(api_key=key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in models:
            if '1.5-flash' in m.lower(): return m
        return models[0] if models else None
    except:
        return None

# 7. Main Logic
if uploaded_file and api_key:
    m_name = get_model(api_key)
    if m_name:
        model = genai.GenerativeModel(m_name)
        
        # Step 1: Transcript
        if st.button("Step 1: Extract Transcript"):
            try:
                with st.spinner("Transcribing..."):
                    if uploaded_file.type.startswith('audio/'):
                        ext = uploaded_file.name.split('.')[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        u_file = genai.upload_file(path=tmp_path)
                        res = model.generate_content(["Provide English word-for-word transcript.", u_file])
                        st.session_state.transcript = res.text
                        os.remove(tmp_path)
                    else:
                        st.session_state.transcript = uploaded_file.read().decode("utf-8")
                    st.success("Done!")
            except Exception as e:
                st.error(f"Error: {e}")

        # Display Transcript
        if st.session_state.transcript:
            st.text_area("Transcript:", st.session_state.transcript, height=200)
            
            # Step 2: Analysis
            if st.button("Step 2: Run Strategic Analysis"):
                try:
                    with st.spinner("Analyzing..."):
                        prompt = f"""
                        You are a Sales Auditor. Respond in English only.
                        Material: {MATERIAL}
                        
                        Structure:
                        ### **Notes**
                        **Call summary:** (Summary)
                        **Situation:** (Context)
                        **Motivation / Pain:** (Why)
                        **Timeline:** (When)
                        **Condition:** (Details)
                        **Price Expectation:** (Price)
                        **Decision Maker:** (Who)
                        **Objections:** (Concerns)
                        **Outcome:** (Next step)
                        **Important Notes:** (Red flags)
                        
                        ---
                        **Strengths:** (Detailed)
                        **Areas to Improve:** (Detailed)
                        **Missed Opportunity:** (Detailed)
                        **Coach Tip:** (Exact script)
                        
                        Transcript: {st.session_state.transcript}
                        """
                        res_analysis = model.generate_content(prompt)
                        st.session_state.analysis = res_analysis.text
                except Exception as e:
                    st.error(f"Error: {e}")

    # Show Final Analysis
    if st.session_state.analysis:
        st.divider()
        st.subheader("🧠 Strategic Audit Report")
        st.markdown(st.session_state.analysis)
        st.download_button("Download (.md)", st.session_state.analysis, file_name="Audit.md")
