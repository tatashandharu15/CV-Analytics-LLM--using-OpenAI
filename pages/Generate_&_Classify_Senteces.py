import streamlit as st
import google.generativeai as genai

# URL Gambar dari Google Drive
logo_url = "logo/Kelompok_5_NautixTech-removebg-preview.png"

# Menampilkan logo di sidebar
st.sidebar.image(logo_url, use_container_width=True)

def configure_model():
    genai.configure(api_key="AIzaSyC_ASWWno13SJlvAPJsACFxgzV8k-zq5Lg")
    return genai.GenerativeModel("gemini-1.5-flash")

# Fungsi untuk mengklasifikasikan kalimat berdasarkan konteks CV
def classify_sentence(model, sentence):
    try:
        response = model.generate_content(f"""
        Berdasarkan kalimat berikut dalam konteks CV, prediksikan kategori kalimat.
        Kategori bisa berupa: 'responsibility', 'requirement', 'skill', 'softskill', 'experience', 'education' atau lainnya.
        
        Kalimat: {sentence}
        
        Kategori:
        """)
        
        return response.text.strip() if hasattr(response, 'text') else "Error: No valid response"
    except Exception as e:
        return f"Error: {e}"

# Fungsi untuk menghasilkan kalimat dalam konteks CV
def generate_sentence(model, category, language):
    try:
        prompt = f"""
        Buatlah sebuah kalimat yang sesuai dengan kategori berikut dalam konteks CV:
        Kategori: {category}
        Bahasa: {language}
        
        Kalimat:
        """
        
        response = model.generate_content(prompt)
        
        return response.text.strip() if hasattr(response, 'text') else "Error: No valid response"
    except Exception as e:
        return f"Error: {e}"

def main():
    st.title("🚀 Sentence Classification and Generation with Gemini")
    model = configure_model()
    
    tab1, tab2 = st.tabs(["Sentence Classification", "Generate Sentence"])
    
    with tab1:
        st.header("Sentence Classification")
        sentence = st.text_area("Input Sentence to Classify:")
        if st.button("Classify Sentence"):
            if sentence:
                category = classify_sentence(model, sentence)
                st.success(f"Prediction Category: {category}")
            else:
                st.warning("Please enter a sentence first.")
    
    with tab2:
        st.header("Generate Sentences by Category")
        category = st.text_input("Enter category to generate sentence:")
        language = st.radio("Choose Language:", ("English", "Indonesian"))
        
        if st.button("Generate Sentence"):
            if category:
                generated_sentence = generate_sentence(model, category, language)
                st.success(f"The resulting sentence: {generated_sentence}")
            else:
                st.warning("Please enter a category first.")

if __name__ == "__main__":
    main()