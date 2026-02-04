import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Strategic Call Auditor Pro", layout="wide", page_icon="🎯")

st.title("🎙️ Strategic Call Auditor & Sales Coach")
st.markdown("Just upload the call below")

# --- المادة التدريبية (المرجع الأساسي للأداة) ---
TRAINING_MATERIAL = """
CORE PILLARS:
1. Motivation: Why they want to sell (serious or nurturing needed).
2. Price: Ask multiple times, uncover expectations.
3. Timeline: When they plan to move (urgency).
4. Condition: Repairs, upgrades, age of systems (Roof, HVAC).
5. Rapport: Trust, mirroring tone, emotional connection.

QUALIFICATION CRITERIA:
- HOT Lead: Motivation + (Price OR Timeline < 30 days).
- WARM Lead: Motivation present but price/timeline not aligned.
- DISQUALIFY: Asking retail/over market, no motivation, not for sale.

OBJECTION HANDLING (CARE Model): Clarify, Acknowledge, Reframe, Explore.
CREDIBILITY: Buying as-is, No realtor fees, Flexible closing, local family-owned.
"""

# --- الشريط الجانبي (الأمان) ---
with st.sidebar:
    st.header("⚙️ Settings")
    gemini_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Get your key: https://aistudio.google.com/app/apikey")
    st.divider()
    st.caption("هذا الموديل مبرمج لتحليل كل كلمة (100% Coverage) واتباع هيكل التقرير بدقة.")

# --- حفظ البيانات في الـ Session ---
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'analysis' not in st.session_state:
    st.session_state.analysis = ""

# --- رفع الملف ---
uploaded_file = st.file_uploader("Upload Audio (wav, mp3) or Text (.txt)", type=['txt', 'wav', 'mp3', 'm4a'])

# دالة اكتشاف الموديل لتجنب أخطاء 404
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
                    with st.spinner("Transcribing content..."):
                        if uploaded_file.type.startswith('audio/'):
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                                tmp_file.write(uploaded_file.getvalue())
                                tmp_path = tmp_file.name
                            audio_file = genai.upload_file(path=tmp_path)
                            response = model.generate_content(["Provide a clear, full word-for-word transcript. No analysis.", audio_file])
                            st.session_state.transcript = response.text
                            os.remove(tmp_path)
                        else:
                            st.session_state.transcript = uploaded_file.read().decode("utf-8")
                        st.success("✅ Transcript Extracted!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        if st.session_state.transcript:
            st.subheader("📄 The Transcript")
            st.text_area("Full Content:", st.session_state.transcript, height=200)
            
            st.divider()

            if st.button("Step 2: Run Strategic Analysis 🚀"):
                try:
                    with st.spinner("Analyzing against material..."):
                        # الـ Prompt المصمم للتنسيق المطلوب حرفياً
                        strategic_prompt = f"""
                        You are a Senior Sales Auditor. Use the Training Material to audit the transcript.
                        
                        TRAINING MATERIAL:
                        {TRAINING_MATERIAL}

                        STRICT FORMATTING RULES:
                        1. EVERY KEY in the 'Notes' section MUST start on a NEW LINE.
                        2. Be extremely detailed in 'Areas to Improve' and 'Missed Opportunity'. 
                        3. 'Coach Tip' must be an exact sentence/script to use.

                        STRICT REPORT STRUCTURE:

                        ### **Notes**
                        **Call summary:** (Provide a brief paragraph summary here)  
                        **Situation:** (New line)  
                        **Motivation / Pain:** (New line)  
                        **Timeline:** (New line)  
                        **Condition (high-level):** (New line)  
                        **Price Expectation + reason:** (New line)  
                        **Decision Maker(s):** (New line)  
                        **Objections / Concerns:** (New line)  
                        **Outcome / Next Step:** (New line)  
                        **Important Notes:** (New line)

                        ---
                        ### **Strategic Audit**

                        **Strength:**
                        - (List detailed strengths based on training)

                        **Areas to Improve:**
                        - (Provide a deep-dive analysis into what went wrong and why)

                        **Missed Opportunity:**
                        - (Detail every pillar or question skipped and the impact of missing it)

                        **Coach Tip:**
                        - (Give the EXACT sentence for the agent to use next time)

                        Transcript:
                        {st.session_state.transcript}
                        """
                        
                        analysis_response = model.generate_content(strategic_prompt)
                        st.session_state.analysis = analysis_response.text
                        st.success("✅ Analysis Complete!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    if st.session_state.analysis:
        st.subheader("🧠 Strategic Audit Report")
        st.markdown(st.session_state.analysis)
        st.download_button("Download Audit (.md)", st.session_state.analysis, file_name="Strategic_Audit.md")

elif not gemini_key and uploaded_file:
    st.warning("Please enter your API Key in the sidebar.")
