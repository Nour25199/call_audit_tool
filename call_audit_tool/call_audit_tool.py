import streamlit as st
import google.generativeai as genai
import tempfile
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="Strategic Auditor Pro", layout="wide")

# 2. إدارة الذاكرة
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'analysis' not in st.session_state:
    st.session_state.analysis = ""
if 'last_file' not in st.session_state:
    st.session_state.last_file = None

st.title("🎙️ AI Strategic Call Auditor")
st.caption("Stable Version (Gemini 1.5 Flash) - English Only")

# 3. Sidebar
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get key: https://aistudio.google.com/app/apikey")

# 4. المادة التدريبية
MATERIAL = """
PILLARS: Motivation, Price, Timeline, Condition, Rapport.
MODELS: CARE (Clarify, Acknowledge, Reframe, Explore).
QUALIFICATION: Hot (2+ criteria), Warm, Long-term.
CREDIBILITY: Local family-owned, A+ BBB, buy as-is, no fees.
"""

# 5. رفع الملف
uploaded_file = st.file_uploader("Upload File", type=['txt', 'wav', 'mp3', 'm4a'])

if uploaded_file and uploaded_file.name != st.session_state.last_file:
    st.session_state.transcript = ""
    st.session_state.analysis = ""
    st.session_state.last_file = uploaded_file.name

# 6. المنطق الرئيسي
if uploaded_file and api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # الخطوة الأولى: الـ Transcript
        if st.button("Step 1: Extract Transcript 📄"):
            try:
                with st.spinner("Processing..."):
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
                    st.success("✅ Transcript Ready!")
            except Exception as e:
                st.error(f"Error in Step 1: {e}")

        # عرض النص لو موجود
        if st.session_state.transcript:
            st.subheader("📄 The Transcript")
            st.text_area("Content:", st.session_state.transcript, height=200)
            
            # الخطوة التانية: التحليل
            if st.button("Step 2: Run Strategic Analysis 🚀"):
                try:
                    with st.spinner("Analyzing..."):
                        prompt = f"""
                        You are a Senior Sales Auditor. Respond in English only.
                        Context: {MATERIAL}
                        
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
                        st.success("✅ Audit Complete!")
                except Exception as e:
                    st.error(f"Error in Step 2: {e}")

        # عرض التقرير النهائي وزر التحميل
        if st.session_state.analysis:
            st.divider()
            st.subheader("🧠 Strategic Audit Report")
            st.markdown(st.session_state.analysis)
            st.download_button("Download Report", st.session_state.analysis, file_name=f"Audit_{uploaded_file.name}.md")

    except Exception as e:
        st.error(f"Config Error: {e}")
