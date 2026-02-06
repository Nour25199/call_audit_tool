import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time

# إعدادات الصفحة
st.set_page_config(page_title="Strategic Auditor Pro", layout="wide")

# إدارة الذاكرة
if 'transcript' not in st.session_state: st.session_state.transcript = ""
if 'analysis' not in st.session_state: st.session_state.analysis = ""
if 'last_file' not in st.session_state: st.session_state.last_file = None

st.title("🎙️ Strategic Call Auditor (Work Mode)")
st.info("Status: Forced Stability Mode (Gemini 1.5 Flash)")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.caption("Using 1.5-Flash to avoid the 20-call daily limit.")

# مادة التدريب
MATERIAL = "PILLARS: Motivation, Price, Timeline, Condition, Rapport. CARE Model for objections."

uploaded_file = st.file_uploader("Upload File", type=['txt', 'wav', 'mp3', 'm4a'])

# تنظيف الذاكرة عند تغيير الملف
if uploaded_file and uploaded_file.name != st.session_state.last_file:
    st.session_state.transcript = ""
    st.session_state.analysis = ""
    st.session_state.last_file = uploaded_file.name

if uploaded_file and api_key:
    try:
        genai.configure(api_key=api_key)
        
        # ⚡ الحل السحري: استدعاء الموديل بأكثر اسم مستقر في 2026
        # نستخدم gemini-1.5-flash-latest لضمان أعلى كوتا (1500 طلب/يوم)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        # Step 1: Transcript
        if st.button("Step 1: Extract Transcript"):
            try:
                with st.spinner("Processing..."):
                    if uploaded_file.type.startswith('audio/'):
                        ext = uploaded_file.name.split('.')[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        u_file = genai.upload_file(path=tmp_path)
                        # انتظار بسيط لضمان معالجة الملف على سيرفر جوجل
                        time.sleep(2) 
                        res = model.generate_content(["Provide a word-for-word English transcript.", u_file])
                        st.session_state.transcript = res.text
                        os.remove(tmp_path)
                    else:
                        st.session_state.transcript = uploaded_file.read().decode("utf-8")
                    st.success("✅ Transcript Ready!")
            except Exception as e:
                # لو لسه فيه 429، ده معناه إن جوجل محتاج دقيقة راحة
                st.error(f"Quota issue? Wait 60 seconds. Details: {e}")

        # Step 2: Analysis
        if st.session_state.transcript:
            st.text_area("Transcript:", st.session_state.transcript, height=200)
            if st.button("Step 2: Run Strategic Analysis"):
                try:
                    with st.spinner("Analyzing..."):
                        prompt = f"""
                        Task: Audit this call in 100% English.
                        Rules: One key per line. Detailed Audit.
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
                        **Strengths:**
                        **Areas to Improve:**
                        **Missed Opportunity:**
                        **Coach Tip:**
                        
                        Context: {MATERIAL}
                        Transcript: {st.session_state.transcript}
                        """
                        res_analysis = model.generate_content(prompt)
                        st.session_state.analysis = res_analysis.text
                        st.success("✅ Analysis Complete!")
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.analysis:
            st.markdown(st.session_state.analysis)
            st.download_button("Download", st.session_state.analysis, file_name="Audit.md")

    except Exception as e:
        st.error(f"Config Error: {e}")
