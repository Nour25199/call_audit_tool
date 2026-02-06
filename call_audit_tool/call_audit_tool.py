import streamlit as st
import google.generativeai as genai
import tempfile
import os

st.set_page_config(page_title="Strategic Auditor Pro 2026", layout="wide")

# إدارة الذاكرة
if 'transcript' not in st.session_state: st.session_state.transcript = ""
if 'analysis' not in st.session_state: st.session_state.analysis = ""
if 'last_file' not in st.session_state: st.session_state.last_file = None

st.title("🎙️ AI Strategic Call Auditor")
st.caption("Auto-Discovery Mode: Detecting Best Available Model in 2026")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get key: https://aistudio.google.com/app/apikey")

# مادة التدريب
MATERIAL = "PILLARS: Motivation, Price, Timeline, Condition, Rapport. CARE Model for objections."

# دالة ذكية للبحث عن الموديل المتاح
def get_working_model(key):
    try:
        genai.configure(api_key=key)
        # بنجيب لستة الموديلات اللي بتدعم توليد المحتوى فعلاً
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # بنرتبهم: بندور على أي حاجة فيها "flash" الأول عشان السرعة والكوتا
        for m in models:
            if 'flash' in m.lower(): return m
        # لو ملقيناش فلاش، ناخد أول موديل متاح (غالباً Pro)
        return models[0] if models else None
    except Exception as e:
        st.sidebar.error(f"Discovery Error: {e}")
        return None

uploaded_file = st.file_uploader("Upload File", type=['txt', 'wav', 'mp3', 'm4a'])

if uploaded_file and uploaded_file.name != st.session_state.last_file:
    st.session_state.transcript = ""
    st.session_state.analysis = ""
    st.session_state.last_file = uploaded_file.name

if uploaded_file and api_key:
    # الكود هنا بيعرف الموديل الشغال لوحده
    selected_model_name = get_working_model(api_key)
    
    if selected_model_name:
        st.sidebar.success(f"Connected to: {selected_model_name}")
        model = genai.GenerativeModel(selected_model_name)
        
        # الخطوة 1: استخراج النص
        if st.button("Step 1: Extract Transcript"):
            try:
                with st.spinner("Processing..."):
                    if uploaded_file.type.startswith('audio/'):
                        ext = uploaded_file.name.split('.')[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        u_file = genai.upload_file(path=tmp_path)
                        res = model.generate_content(["Provide word-for-word English transcript.", u_file])
                        st.session_state.transcript = res.text
                        os.remove(tmp_path)
                    else:
                        st.session_state.transcript = uploaded_file.read().decode("utf-8")
                    st.success("Done!")
            except Exception as e:
                st.error(f"Error: {e}")

        # الخطوة 2: التحليل
        if st.session_state.transcript:
            st.text_area("Transcript:", st.session_state.transcript, height=200)
            if st.button("Step 2: Run Analysis"):
                try:
                    with st.spinner("Analyzing..."):
                        prompt = f"Audit this call based on: {MATERIAL}. Transcript: {st.session_state.transcript}"
                        res_analysis = model.generate_content(prompt)
                        st.session_state.analysis = res_analysis.text
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.analysis:
            st.markdown(st.session_state.analysis)
            st.download_button("Download Report", st.session_state.analysis, file_name="Audit.md")
    else:
        st.error("No models found. Check your API Key or Google AI Studio access.")
