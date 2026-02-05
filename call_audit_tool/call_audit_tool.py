import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Strategic Auditor Pro", layout="wide", page_icon="🎯")

# --- 2. إدارة الذاكرة (Session State) ---
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'analysis' not in st.session_state:
    st.session_state.analysis = ""
if 'last_file' not in st.session_state:
    st.session_state.last_file = None

st.title("🎙️ AI Strategic Call Auditor")
st.markdown("Stable Version (Gemini 1.5 Flash) - 1500 Requests/Day")

# --- 3. الشريط الجانبي ---
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get your key: https://aistudio.google.com/app/apikey")
    st.divider()
    st.caption("Using Gemini 1.5 Flash for maximum stability and daily quota.")

# --- 4. المادة التدريبية (Material) ---
TRAINING_MATERIAL = """
PILLARS: Motivation (Why), Price (Uncover expectations), Timeline (Urgency), Condition (Repairs/Age), Rapport (Trust/Mirroring).
MODELS: CARE (Clarify, Acknowledge, Reframe, Explore).
QUALIFICATION: Hot (Motivation + Price/Timeline < 30 days), Warm, Long-term.
CREDIBILITY: Local family-owned, 6+ years experience, A+ BBB, buy as-is, no fees, flexible closing.
"""

uploaded_file = st.file_uploader("Upload Audio or Text", type=['txt', 'wav', 'mp3', 'm4a'])

# مسح البيانات لو الملف اتغير
if uploaded_file and uploaded_file.name != st.session_state.last_file:
    st.session_state.transcript = ""
    st.session_state.analysis = ""
    st.session_state.last_file = uploaded_file.name

# --- 5. المنطق الرئيسي (Main Logic) ---
if uploaded_file and api_key:
    try:
        genai.configure(api_key=api_key)
        # إجبار الكود على استخدام 1.5 Flash لتجنب ليميت الـ 20 طلب
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # الخطوة 1: استخراج النص
        if st.button("Step 1: Extract Transcript 📄"):
            try:
                with st.spinner("Processing file..."):
                    if uploaded_file.type.startswith('audio/'):
                        ext = uploaded_file.name.split('.')[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        u_file = genai.upload_file(path=tmp_path)
                        res = model.generate_content(["Provide English word-for-word transcript. No summary.", u_file])
                        st.session_state.transcript = res.text
                        os.remove(tmp_path)
                    else:
                        st.session_state.transcript = uploaded_file.read().decode("utf-8")
                    st.success("✅ Transcript Ready!")
            except Exception as e:
                st.error(f"Error in Step 1: {str(e)}")

        # عرض النص
        if st.session_state.transcript:
            st.subheader("📄 The Transcript")
            st.text_area("Content:", st.session_state.transcript, height=200)
            
            st.divider()

            # الخطوة 2: التحليل الاستراتيجي
            if st.button("Step 2: Run Strategic Analysis 🚀"):
                try:
                    with st.spinner("Analyzing against training material..."):
                        prompt = f"""
                        You are a Senior Real Estate Sales Auditor. 
                        LANGUAGE: English only. No Arabic.
                        
                        This audit is based on lead manager training materials (Pillars, CARE, Credibility).

                        STRICT FORMAT: 
                        One key per line in the Notes section. Be very detailed in Audit sections.

                        ### **Notes**
                        **Call summary:** (Summary)
                        **Situation:** (Context)
                        **Motivation / Pain:** (Why)
                        **Timeline:** (When)
                        **Condition (high-level):** (Details)
                        **Price Expectation + reason:** (Price logic)
                        **Decision Maker(s):** (Who)
                        **Objections / Concerns:** (Concerns)
                        **Outcome / Next Step:** (Plan)
                        **Important Notes:** (Red flags)

                        ---
                        ### **Strengths**
                        - (Detailed strengths based on training)
                        
                        ---
                        ### **Areas to Improve (Detailed)**
                        - (Detailed analysis of failures)
                        
                        ---
                        ### **Missed Opportunity (Detailed)**
                        - (Specific points skipped)
                        
                        ---
                        ### **Coach Tip (Exact sentence/question to use next time)**
                        - (Exact script based on material)

                        Material: {TRAINING_MATERIAL}
                        Transcript: {st.session_state.transcript}
                        """
                        res_analysis = model.generate_content(prompt)
                        st.session_state.analysis = res_analysis.text
                        st.success("✅ Analysis Complete!")

        # عرض التحليل النهائي
        if st.session_state.analysis:
            st.subheader("🧠 Strategic Audit Report")
            st.markdown(st.session_state.analysis)
            st.download_button("Download Report (.md)", st.session_state.analysis, file_name=f"Audit_{uploaded_file.name}.md")

    except Exception as e:
        st.error(f"Configuration Error: {e}")
