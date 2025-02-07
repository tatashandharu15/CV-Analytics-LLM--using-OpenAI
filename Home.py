import streamlit as st
from PIL import Image

def main():
    st.set_page_config(page_title="AI CV Analysis", layout="wide")
    
    st.title("🚀 AI-Powered CV Analysis")
    st.write("Selamat datang di aplikasi AI untuk analisis CV!")

    image = Image.open("logo/Kelompok_5_NautixTech-removebg-preview.png")
    st.image(image, use_container_width=True)
    
    st.markdown("""
    ### 🔥 Fitur Utama:
    - **CV Rating**: Analisis CV berdasarkan kategori seperti skill, pengalaman, dan pendidikan.
    - **HR Review**: Cocokkan CV dengan persyaratan HRD dan peringkat kandidat terbaik.
    - **Chatbot AI**: Dapatkan saran perbaikan dan rekomendasi untuk CV Anda.
    """)

if __name__ == "__main__":
    main()