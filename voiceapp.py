import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import os
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr

st.set_page_config(page_title="Traducteur Vocal", page_icon="🎤", layout="wide")

LANGUAGES = {
    "Français": {"code": "fr", "recognition": "fr-FR", "flag": "🇫🇷"},
    "Anglais": {"code": "en", "recognition": "en-US", "flag": "🇺🇸"},
    "Espagnol": {"code": "es", "recognition": "es-ES", "flag": "🇪🇸"},
    "Swahili": {"code": "sw", "recognition": "sw-KE", "flag": "🇰🇪"},
    "Arabe": {"code": "ar", "recognition": "ar-SA", "flag": "🇸🇦"},
    "Allemand": {"code": "de", "recognition": "de-DE", "flag": "🇩🇪"},
    "Italien": {"code": "it", "recognition": "it-IT", "flag": "🇮🇹"},
    "Portugais": {"code": "pt", "recognition": "pt-PT", "flag": "🇵🇹"},
}

def record_audio(duration=5, samplerate=44100):
    st.info("🎤 Enregistrement en cours...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    st.success("✅ Enregistrement terminé")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp_file.name, samplerate, audio)
    return temp_file.name

def transcribe_audio(file_path, language_code):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    return recognizer.recognize_google(audio_data, language=language_code)

def translate_text(text, source_lang, target_lang):
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    return translator.translate(text)

def text_to_speech(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

st.title("🎤 Traducteur Vocal Intelligent (Compatible Cloud)")

col1, col2 = st.columns(2)
source_lang = col1.selectbox("Langue source", list(LANGUAGES.keys()))
target_lang = col2.selectbox("Langue cible", [l for l in LANGUAGES.keys() if l != source_lang])

duration = st.slider("Durée d'enregistrement (sec)", 2, 10, 5)

if st.button("🎙️ Enregistrer, traduire et écouter"):
    audio_file = record_audio(duration)
    st.audio(audio_file)

    try:
        text = transcribe_audio(audio_file, LANGUAGES[source_lang]["recognition"])
        st.success(f"Texte reconnu ({source_lang}) : {text}")

        translated = translate_text(text, LANGUAGES[source_lang]["code"], LANGUAGES[target_lang]["code"])
        st.success(f"Traduction ({target_lang}) : {translated}")

        audio_trad = text_to_speech(translated, LANGUAGES[target_lang]["code"])
        st.audio(audio_trad, format="audio/mp3")

        os.unlink(audio_file)
        os.unlink(audio_trad)
    except Exception as e:
        st.error(f"Erreur : {e}")
