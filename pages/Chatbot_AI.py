import streamlit as st
import google.generativeai as genai


# URL Gambar dari Google Drive
logo_url = "logo/Kelompok_5_NautixTech-removebg-preview.png"

# Menampilkan logo di sidebar
st.sidebar.image(logo_url, use_container_width=True)

def configure_model():
    genai.configure(api_key="AIzaSyC_ASWWno13SJlvAPJsACFxgzV8k-zq5Lg")
    return genai.GenerativeModel("gemini-1.5-flash")

# Fungsi untuk memberikan saran CV
def suggest_cv_improvements(model, text):
    try:
        response = model.generate_content(f"""
        Berdasarkan teks berikut, saran apa yang perlu dilakukan dalam CV.
        
        Teks: {text}
        
        Saran:
        """)
        return response.text.strip() if hasattr(response, 'text') else "Error: No valid response"
    except Exception as e:
        return f"Error: {e}"

# Fungsi untuk memprediksi kategori CV
def predict_cv_category(model, text):
    try:
        response = model.generate_content(f"""
        Berdasarkan teks berikut, prediksikan kategori CV.
        Kategori bisa berupa: 'responsibility', 'requirement', 'skill', 'softskill', 'experience', 'education' atau lainnya.
        
        Teks: {text}
        
        Kategori:
        """)
        return response.text.strip() if hasattr(response, 'text') else "Error: No valid response"
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.title("🤖 CV Analysis Chatbot")
model = configure_model()

option = st.radio("Pilih mode analisis:", ["Saran CV", "Prediksi Kategori CV"])
text_input = st.text_area("Masukkan teks CV:")

if st.button("Analisis"):
    if text_input.strip():
        if option == "Saran CV":
            result = suggest_cv_improvements(model, text_input)
        else:
            result = predict_cv_category(model, text_input)
        st.write("### Hasil:")
        st.write(result)
    else:
        st.warning("Silakan masukkan teks CV terlebih dahulu.")