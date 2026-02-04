import streamlit as st
import google.generativeai as genai
import tempfile
import os

st.set_page_config(page_title="Strategic Analyzer 2026", layout="wide", page_icon="🚀")

st.title("🎙️ Strategic Transcript & Analysis Tool")

with st.sidebar:
    st.header("⚙️ Settings")
    gemini_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("احصل على مفتاحك من: https://aistudio.google.com/app/apikey")

if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'analysis' not in st.session_state:
    st.session_state.analysis = ""

uploaded_file = st.file_uploader("Upload Audio or Text", type=['txt', 'wav', 'mp3', 'm4a'])

# دالة لاكتشاف أفضل موديل متاح في حسابك حالياً
def find_best_model(api_key):
    try:
        genai.configure(api_key=api_key)
        # بنجيب لستة الموديلات اللي حسابك يقدر يوصل لها
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # الأولوية للـ Flash عشان السرعة، ثم الـ Pro
        for m_name in available_models:
            if 'flash' in m_name.lower(): return m_name
        for m_name in available_models:
            if 'pro' in m_name.lower(): return m_name
        
        return available_models[0] if available_models else None
    except Exception as e:
        st.error(f"Failed to list models: {str(e)}")
        return None

if uploaded_file and gemini_key:
    # اكتشاف الموديل المناسب فوراً
    model_name = find_best_model(gemini_key)
    
    if not model_name:
        st.error("❌ لا يمكن العثور على موديلات متاحة. تأكد من صحة الـ API Key.")
    else:
        st.caption(f"Connected to: `{model_name}`")
        model = genai.GenerativeModel(model_name)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Step 1: Extract Transcript 📄"):
                try:
                    with st.spinner("Processing..."):
                        if uploaded_file.type.startswith('audio/'):
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_path = tmp_file.name

                            audio_file = genai.upload_file(path=tmp_path)
                            # نطلب منه يعمل Transcript دقيق
                            response = model.generate_content([
                                "You are a professional transcriber. Convert this audio into a full, accurate, word-for-word text transcript. Do not summarize.", 
                                audio_file
                            ])
                            st.session_state.transcript = response.text
                            os.remove(tmp_path)
                        else:
                            st.session_state.transcript = uploaded_file.read().decode("utf-8")
                        st.success("✅ Transcript Extracted!")
                except Exception as e:
                    st.error(f"Error in Step 1: {str(e)}")

        if st.session_state.transcript:
            st.subheader("📄 The Transcript")
            st.text_area("Copy transcript here:", st.session_state.transcript, height=250)
            
            st.divider()

            if st.button("Step 2: Run Strategic Analysis 🚀"):
                try:
                    with st.spinner("Analyzing deep insights..."):
                        prompt = (
                            "You are a Senior Strategic Analyst. Analyze 100% of the provided transcript.\n"
                            "STRICT RULES:\n"
                            "1. NO section numbers, timestamps, or numerical references.\n"
                            "2. Extract ALL Strengths and ALL Weaknesses found in the text.\n"
                            "3. Structure: ## Executive Summary, ## Strengths, ## Weaknesses, ## Final Strategic Verdict.\n"
                            f"\nTranscript:\n{st.session_state.transcript}"
                        )
                        analysis_response = model.generate_content(prompt)
                        st.session_state.analysis = analysis_response.text
                        st.success("✅ Analysis Complete!")
                except Exception as e:
                    st.error(f"Error in Step 2: {str(e)}")

        if st.session_state.analysis:
            st.subheader("🧠 Strategic Analysis Report")
            st.markdown(st.session_state.analysis)
            st.download_button("Download Report (.md)", st.session_state.analysis, file_name="Strategic_Analysis.md")

