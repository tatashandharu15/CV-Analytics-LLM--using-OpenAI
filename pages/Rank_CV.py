import streamlit as st
import google.generativeai as genai
import pdfplumber
import os
import matplotlib.pyplot as plt
import pandas as pd
import json

# Konfigurasi API Google Gemini
api_key = "AIzaSyC_ASWWno13SJlvAPJsACFxgzV8k-zq5Lg"  # Ganti dengan API key Anda
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")


# URL Gambar dari Google Drive
logo_url = "logo/Kelompok_5_NautixTech-removebg-preview.png"

# Menampilkan logo di sidebar
st.sidebar.image(logo_url, use_container_width=True)

# Fungsi untuk ekstraksi teks dari PDF
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

# Streamlit UI
st.title("📈 Rank Multiple CVs 📉")
st.write("Upload up to 5 CVs in PDF format for ranking.")

uploaded_files = st.file_uploader("Upload CVs (PDF)", type=["pdf"], accept_multiple_files=True, key="file_uploader")

if uploaded_files:
    results = []
    for uploaded_file in uploaded_files[:5]:
        temp_pdf_path = f"temp_{uploaded_file.name}"
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.read())
        
        extracted_text = extract_text_from_pdf(temp_pdf_path)
        category_dict = classify_text(extracted_text)
        
        if "error" not in category_dict:
            results.append({"file": uploaded_file.name, **category_dict})
        
        os.remove(temp_pdf_path)
    
    if results:
        df = pd.DataFrame(results)
        
        # Mengisi NaN dengan 0 untuk menghindari kesalahan konversi
        df.fillna(0, inplace=True)

        st.subheader("Classification Results:")
        st.dataframe(df)
        
        selected_category = st.selectbox("Select category to rank:", df.columns[1:])
        
        # Pastikan nilai kategori bertipe numerik sebelum perhitungan
        df[selected_category] = pd.to_numeric(df[selected_category], errors='coerce').fillna(0)
        
        ranked_df = df.sort_values(by=selected_category, ascending=False)
        st.subheader(f"Ranking by {selected_category}:")
        st.dataframe(ranked_df)
        
        # Bar chart untuk perangkingan
        st.subheader(f"Bar Chart Ranking by {selected_category}")
        fig, ax = plt.subplots()
        ax.barh(ranked_df['file'], ranked_df[selected_category], color='skyblue')
        ax.set_xlabel('Score')
        ax.set_ylabel('File')
        ax.set_title(f'Ranking by {selected_category}')
        st.pyplot(fig)
        
        # Pie chart per file
        for index, row in ranked_df.iterrows():
            labels = row.index[1:]
            sizes = row[1:].values
            
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax.axis('equal')
            
            st.subheader(f"{row['file']} Classification")
            st.pyplot(fig)
