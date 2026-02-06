import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Strategic Auditor Pro", layout="wide", page_icon="🎯")

# --- 2. إدارة الذاكرة ---
if 'transcript' not in st.session_state: st.session_state.transcript = ""
if 'analysis' not in st.session_state: st.session_state.analysis = ""
if 'last_file' not in st.session_state: st.session_state.last_file = None

st.title("🎙️ AI Strategic Call Auditor")
st.caption("2026 Adaptive Mode: Auto-detecting available models...")

# --- 3. الشريط الجانبي ---
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get key: https://aistudio.google.com/app/apikey")
    st.divider()
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # دالة للبحث عن الموديلات المتاحة في حسابك حالياً
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.write("Found Models:", available_models)
        except:
            st.error("Invalid Key or Connection Error")

# --- 4. المادة التدريبية ---
MATERIAL = "PILLARS: Motivation, Price, Timeline, Condition, Rapport. CARE Model for objections."

# --- 5. دالة اختيار الموديل "المنقذة" ---
def select_model(api_key):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # الأولوية رقم 1: البحث عن أي موديل 1.5 فلاش (لأنه 1500 طلب/يوم)
        for m in models:
            if '1.5-flash' in m.lower(): return m
        
        # الأولوية رقم 2: أي موديل فلاش متاح (2.0 أو غيره)
        for m in models:
            if 'flash' in m.lower(): return m
            
        # الأولوية رقم 3: أول موديل متاح في القائمة
        return models[0] if models else None
    except:
        return None

uploaded_file = st.file_uploader("Upload File", type=['txt', 'wav', 'mp3', 'm4a'])

if uploaded_file and uploaded_file.name != st.session_state.last_file:
    st.session_state.transcript = ""
    st.session_state.analysis = ""
    st.session_state.last_file = uploaded_file.name

# --- 6. المنطق الرئيسي ---
if uploaded_file and api_key:
    model_name = select_model(api_key)
    
    if model_name:
        model = genai.GenerativeModel(model_name)
        
        # الخطوة 1: النص
        if st.button("Step 1: Extract Transcript"):
            try:
                with st.spinner(f"Using {model_name}..."):
                    if uploaded_file.type.startswith('audio/'):
                        ext = uploaded_file.name.split('.')[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        u_file = genai.upload_file(path=tmp_path)
                        # انتظار أمان لسيرفرات جوجل
                        time.sleep(3) 
                        res = model.generate_content(["Provide word-for-word transcript in English.", u_file])
                        st.session_state.transcript = res.text
                        os.remove(tmp_path)
                    else:
                        st.session_state.transcript = uploaded_file.read().decode("utf-8")
                    st.success(f"✅ Ready with {model_name}!")
            except Exception as e:
                st.error(f"Error: {e}")

        # الخطوة 2: التحليل
        if st.session_state.transcript:
            st.text_area("Transcript:", st.session_state.transcript, height=200)
            if st.button("Step 2: Run Strategic Analysis"):
                try:
                    with st.spinner("Analyzing..."):
                        prompt = f"Audit this call based on {MATERIAL}. Transcript: {st.session_state.transcript}"
                        res_analysis = model.generate_content(prompt)
                        st.session_state.analysis = res_analysis.text
                        st.success("✅ Analysis Complete!")
                except Exception as e:
                    st.error(f"Analysis Error: {e}")

        if st.session_state.analysis:
            st.markdown(st.session_state.analysis)
            st.download_button("Download", st.session_state.analysis, file_name="Audit.md")
    else:
        st.error("No compatible models found on your account. Check AI Studio settings.")
