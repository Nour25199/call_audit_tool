import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Strategic Call Auditor Pro", layout="wide", page_icon="🎯")

st.title("🎙️ Strategic Call Auditor & Sales Coach")
st.markdown("Just upload your call below")

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
        available_models = [m.name for
