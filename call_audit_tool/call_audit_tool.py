import streamlit as st
import google.generativeai as genai
import tempfile
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="Strategic Auditor 2026", layout="wide")

# 2. إدارة الذاكرة
if 'transcript' not in st.session_state: st.session_state.transcript = ""
if 'analysis' not in st.session_state: st.session_state.analysis = ""

st.title("🎙️ AI Strategic Call Auditor")

# 3. الشريط الجانبي (Sidebar)
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get key: https://aistudio.google.com/app/apikey")

# 4. المادة التدريبية (Material)
MATERIAL = "PILLARS: Motivation, Price, Timeline, Condition, Rapport. CARE Model for objections."

# 5. دالة "البحث عن موديل شغال" (Anti-404)
def get_working_model(key):
    try:
        genai.configure(api_key=key)
        # بنجيب كل الموديلات المتاحة في حسابك حالياً
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # بننقي الـ 1.5 فلاش أو أي فلاش متاح عشان الكوتا
                if '1.5-flash' in m.name.lower():
                    return m.name
        # لو ملقيناش 1.5، ناخد أول واحد متاح وخلاص
        return "gemini-1.5-flash" 
    except:
        return None

uploaded_file = st.file_uploader("Upload File", type=['txt', 'wav', 'mp3', 'm4a'])

# 6. التنفيذ
if uploaded_file and api_key:
    try:
        model_name = get_working_model(api_key)
        model = genai.GenerativeModel(model_name)
        
        # الخطوة 1: الترجمة
        if st.button("Step 1: Extract Transcript"):
            try:
                with st.spinner(f"Using {model_name}..."):
                    if uploaded_file.type.startswith('audio/'):
                        ext = uploaded_file.name.split('.')[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name
                        
                        u_file = genai.upload_file(path=tmp_path)
                        res = model.generate_content(["Provide word-for-word transcript.", u_file])
                        st.session_state.transcript = res.text
                        os.remove(tmp_path)
                    else:
                        st.session_state.transcript = uploaded_file.read().decode("utf-8")
                    st.success("✅ Done!")
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
                        st.success("✅ Audit Complete!")
                except Exception as e:
                    st.error(f"Error: {e}")

        if st.session_state.analysis:
            st.markdown(st.session_state.analysis)
            st.download_button("Download Report", st.session_state.analysis, file_name="Audit.md")

    except Exception as e:
        st.error(f"Config Error: {e}")
