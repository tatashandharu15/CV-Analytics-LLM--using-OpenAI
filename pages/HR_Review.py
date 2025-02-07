import streamlit as st
import google.generativeai as genai
import pdfplumber
import os
import matplotlib.pyplot as plt
import pandas as pd
import json
import seaborn as sns
from difflib import SequenceMatcher

# Konfigurasi API Google Gemini
api_key = "AIzaSyC_ASWWno13SJlvAPJsACFxgzV8k-zq5Lg"
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Fungsi ekstraksi teks dari PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text.strip()

# Fungsi untuk klasifikasi teks
def classify_text(text):
    try:
        input_text = f"""
        Berdasarkan isi CV berikut, prediksikan kategori CV.
        Kategori bisa berupa: 'responsibility', 'requirement', 'skill', 'softskill', 'experience', 'education' atau lainnya.
        Berikan output dalam format JSON seperti contoh berikut:
        ```json
        {{
            "responsibility": 30,
            "requirement": 20,
            "skill": 25,
            "softskill": 10,
            "experience": 10,
            "education": 5
        }}
        ```
        Hanya berikan JSON tanpa teks tambahan.
        Teks:
        """
        input_text += text
        
        response = model.generate_content(input_text)
        response_text = response.text.strip() if response and hasattr(response, 'text') else "{}"
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            category_dict = json.loads(response_text)
            if isinstance(category_dict, dict) and all(isinstance(v, (int, float)) for v in category_dict.values()):
                return category_dict
            else:
                return {"error": "Format JSON tidak sesuai."}
        except json.JSONDecodeError:
            return {"error": "Respons dari model bukan JSON yang valid."}
    except Exception as e:
        return {"error": str(e)}

# Fungsi untuk menghitung kesesuaian teks dengan requirement HRD
def similarity_score(text, requirement):
    return SequenceMatcher(None, text.lower(), requirement.lower()).ratio() * 100

# Streamlit UI
st.set_page_config(page_title="CV Classifier App", layout="wide")
st.title("📊 CV Classifier App 📄")
st.write("Upload up to 5 CVs in PDF format to find the best match.")

# URL Gambar dari Google Drive
logo_url = "logo/Kelompok_5_NautixTech-removebg-preview.png"

# Menampilkan logo di sidebar
st.sidebar.image(logo_url, use_container_width=True)

hrd_requirements = st.text_area("Enter HRD Requirements:", "")

uploaded_files = st.file_uploader("Upload CVs (PDF, max 5 files)", type=["pdf"], accept_multiple_files=True, help="You can upload up to 5 PDF files.")

if uploaded_files and hrd_requirements:
    results = {}
    matching_scores = []
    
    for uploaded_file in uploaded_files:
        temp_pdf_path = uploaded_file.name
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.read())
        
        extracted_text = extract_text_from_pdf(temp_pdf_path)
        category_dict = classify_text(extracted_text)
        os.remove(temp_pdf_path)
        
        if "error" not in category_dict:
            results[uploaded_file.name] = category_dict
            match_score = similarity_score(extracted_text, hrd_requirements)
            matching_scores.append({"CV": uploaded_file.name, "Match Score": match_score})
    
    if results:
        st.subheader("📊 Classification Results")
        df_matching = pd.DataFrame(matching_scores).sort_values(by="Match Score", ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x="Match Score", y="CV", data=df_matching, palette="Blues_r", ax=ax)
        ax.set_title("Ranking of CVs based on HRD Requirement Match Score")
        ax.set_xlabel("Match Score (%)")
        
        st.dataframe(df_matching, hide_index=True)
        st.pyplot(fig)
