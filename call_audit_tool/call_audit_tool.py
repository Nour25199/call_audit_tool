import streamlit as st
import google.generativeai as genai
import tempfile
import os

st.set_page_config(page_title="Strategic Call Auditor Pro", layout="wide", page_icon="🎯")

# --- ميزة مسح الذاكرة عند تغيير الملف ---
if 'last_uploaded_file' not in st.session_state:
    st.session_state.last_uploaded_file = None

# --- إعدادات الحالة (State) ---
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'analysis' not in st.session_state:
    st.session_state.analysis = ""

st.title("🎙️ Strategic Call Auditor & Sales Coach")

with st.sidebar:
    st.header("⚙️ Settings")
    # الـ Key هيفضل موجود طول ما إنت فاتح التاب ومش هتحتاج تكتبه تاني
    gemini_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get your key: https://aistudio.google.com/app/apikey")

# --- المادة التدريبية (TRAINING_MATERIAL) ---
TRAINING_MATERIAL = """ [نفس المادة التدريبية اللي حطيناها قبل كدة] """

uploaded_file = st.file_uploader("Upload Audio (wav, mp3) or Text (.txt)", type=['txt', 'wav', 'mp3', 'm4a'])

# ✨ الحركة السحرية: لو الملف اتغير، امسح كل التحليلات القديمة فوراً
if uploaded_file is not None:
    if uploaded_file.name != st.session_state.last_uploaded_file:
        st.session_state.transcript = ""
        st.session_state.analysis = ""
        st.session_state.last_uploaded_file = uploaded_file.name
        # ده بيخلي الصفحة تنضف أول ما ترفع ملف جديد

# --- بقية الكود (دالة الموديل والتحليل) ---
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
                        st.success("✅ Transcript Ready for the new file!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        if st.session_state.transcript:
            st.subheader("📄 The Transcript")
            st.text_area("Full Content:", st.session_state.transcript, height=200)
            
            st.divider()

            if st.button("Step 2: Run Strategic Analysis 🚀"):
                try:
                    with st.spinner("Analyzing..."):
                        # [نفس الـ Prompt المطور اللي عملناه بخصوص الـ Structure والسطور الجديدة]
                        strategic_prompt = f""" [البرومبت اللي فيه الـ formatting بتاعك] """
                        
                        analysis_response = model.generate_content(strategic_prompt)
                        st.session_state.analysis = analysis_response.text
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    if st.session_state.analysis:
        st.subheader("🧠 Strategic Audit Report")
        st.markdown(st.session_state.analysis)
        st.download_button("Download Audit (.md)", st.session_state.analysis, file_name=f"Audit_{uploaded_file.name}.md")
