import streamlit as st
import google.generativeai as genai
import pdfplumber
import os
import matplotlib.pyplot as plt
import json
import urllib.parse


# URL Gambar dari Google Drive (sesuaikan jika perlu)
logo_url = "logo/Kelompok_5_NautixTech-removebg-preview.png"


# Menampilkan logo di sidebar
st.sidebar.image(logo_url, use_container_width=True)


# Konfigurasi API Google Gemini
api_key = "AIzaSyC_ASWWno13SJlvAPJsACFxgzV8k-zq5Lg"  # Ganti dengan API key Anda
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")


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


# Fungsi untuk mencari lowongan kerja
def search_job_links(role, skills):
   base_urls = {
       "Glints": "https://glints.com/id/opportunities/jobs/explore?keyword=",
       # "JobStreet": "https://www.jobstreet.com/id/",
       "LinkedIn Jobs": "https://www.linkedin.com/jobs/search?keywords=",
   }


   query = urllib.parse.quote_plus(f"{role}")
   job_links = {platform: f"{url}{query}" for platform, url in base_urls.items()}
   return job_links


# Fungsi untuk merekomendasikan role pekerjaan dengan link
def recommend_job(text):
   try:
       input_text = f"""
       Berdasarkan isi CV berikut, berikan rekomendasi pekerjaan yang cocok.
       Berikan hasil dalam format JSON seperti contoh berikut:
       ```json
       {{
           "role": "Data Scientist",
           "skills": ["Python", "Machine Learning", "Data Analysis"],
           "tools": ["TensorFlow", "Scikit-Learn", "SQL"],
           "jobdesc": "Menganalisis data dan membangun model prediksi untuk mendukung keputusan bisnis."
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
           job_info = json.loads(response_text)
           if isinstance(job_info, dict):
               # Tambahkan link lowongan kerja
               job_info["job_links"] = search_job_links(job_info["role"], job_info["skills"])
               return job_info
           else:
               return {"error": "Format JSON tidak sesuai."}
       except json.JSONDecodeError:
           return {"error": "Respons dari model bukan JSON yang valid."}
   except Exception as e:
       return {"error": str(e)}


# Streamlit UI
st.title("🔥 Check Your CV Performance 🔥")
st.write("Upload your CV file in PDF format for classification.")


uploaded_file = st.file_uploader("Upload CV (PDF)", type=["pdf"])


if uploaded_file is not None:
   temp_pdf_path = "temp_cv.pdf"
   with open(temp_pdf_path, "wb") as f:
       f.write(uploaded_file.read())


   extracted_text = extract_text_from_pdf(temp_pdf_path)
   st.subheader("Extracted text:")
   st.text_area("Text CV:", extracted_text, height=200, label_visibility="collapsed")


   if st.button("Classify"):
       with st.spinner("Processing classification..."):
           category_dict = classify_text(extracted_text)
           st.session_state.category_dict = category_dict
           if "error" in category_dict:
               st.write("Terjadi kesalahan dalam klasifikasi:", category_dict["error"])
           else:
               labels = list(category_dict.keys())
               sizes = list(category_dict.values())
               fig, ax = plt.subplots()
               ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
               ax.axis('equal')
               st.subheader("Classification Results:")
               st.write(category_dict)
               st.pyplot(fig)


   if st.button("Get Job Recommendation"):
       with st.spinner("Fetching job recommendations..."):
           recommended_job = recommend_job(extracted_text)
           if "error" in recommended_job:
               st.write("Terjadi kesalahan dalam rekomendasi:", recommended_job["error"])
           else:
               st.subheader("Recommended Job Role:")
               st.write(f"**Role:** {recommended_job['role']}")
               st.write(f"**Skills Required:** {', '.join(recommended_job['skills'])}")
               st.write(f"**Tools Used:** {', '.join(recommended_job['tools'])}")
               st.write(f"**Job Description:** {recommended_job['jobdesc']}")


               # Menampilkan link lowongan kerja
               if "job_links" in recommended_job:
                   st.subheader("🔍 Job Opportunities:")
                   for platform, link in recommended_job["job_links"].items():
                       st.markdown(f"[🔗 {platform}]({link})", unsafe_allow_html=True)


   os.remove(temp_pdf_path)