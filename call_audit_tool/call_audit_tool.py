import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Strategic Auditor 2026", layout="wide")

# --- 2. إدارة الذاكرة ---
if 'transcript' not in st.session_state: st.session_state.transcript = ""
if 'analysis' not in st.session_state: st.session_state.analysis = ""
if 'last_file' not in st.session_state: st.session_state.last_file = None

st.title("🎙️ AI Strategic Call Auditor")
st.markdown("---")

# --- 3. الشريط الجانبي (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Enter NEW Gemini API Key", type="password")
    st.info("Get key from NEW account: https://aistudio.google.com/app/apikey")

# --- 4. دالة البحث التلقائي عن الموديل (تمنع الـ 404) ---
def get_model_safely(key):
    try:
        genai.configure(api_key=key)
        # بنجيب لستة بكل الموديلات المتاحة للحساب ده
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # الأولوية للـ 1.5 فلاش عشان الكوتا (1500 طلب)
        for m in models:
            if '1.5-flash' in m.lower(): return m
        # لو ملقيناش، ناخد أي فلاش متاح (زي 2.0)
        for m in models:
            if 'flash' in m.lower(): return m
        return models[0] if models else None
    except:
        return None

# --- 5. المادة التدريبية (Material) ---
MATERIAL = "PILLARS: Motivation, Price, Timeline, Condition, Rapport. CARE Model for objections."

uploaded_file = st.file_uploader("Upload Audio or Text", type=['txt', 'wav', 'mp3', 'm4a'])

# مسح القديم لو رفعنا ملف جديد
if uploaded_file and uploaded_file.name != st.session_state.last_file:
    st.session_state.transcript = ""
    st.session_state.analysis = ""
    st.session_state.last_file = uploaded_file.name

# --- 6. المنطق الرئيسي ---
if uploaded_file and api_key:
    selected_model = get_model_safely(api_key)
    
    if selected_model:
        model = genai.GenerativeModel(selected_model)
        
        # الخطوة 1: استخراج النص
        if st.button("Step 1: Extract Transcript 📄"):
            try:
                with st.spinner(f"Using {selected_model}..."):
                    if uploaded_file.type.startswith('audio/'):
                        ext = uploaded_file.name.split('.')[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        u_file = genai.upload_file(path=tmp_path)
                        res = model.generate_content(["Provide word-for-word transcript in English.", u_file])
                        st.session_state.transcript = res.text
                        os.remove(tmp_path)
                    else:
                        st.session_state.transcript = uploaded_file.read().decode("utf-8")
                    st.success(f"✅ Success! Connected via {selected_model}")
            except Exception as e:
                st.error(f"Error: {e}")

        # الخطوة 2: التحليل
        if st.session_state.transcript:
            st.text_area("Transcript:", st.session_state.transcript, height=200)
            if st.button("Step 2: Run Strategic Analysis 🚀"):
                try:
                    with st.spinner("Analyzing..."):
                        prompt = f"Audit this call based on {MATERIAL}. Transcript: {st.session_state.transcript}"
                        res_analysis = model.generate_content(prompt)
                        st.session_state.analysis = res_analysis.text
                        st.success("✅ Audit Complete!")
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.analysis:
            st.markdown(st.session_state.analysis)
            st.download_button("Download Report", st.session_state.analysis, file_name="Audit.md")
    else:
        st.error("Could not find any available models. Check your API Key.")
