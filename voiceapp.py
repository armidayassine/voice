import streamlit as st
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile
import os
import io

# Configuration de la page
st.set_page_config(
    page_title="Traducteur Vocal",
    page_icon="🎤",
    layout="wide"
)

# Dictionnaire des langues supportées
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

def transcribe_speech(language_code):
    """Fonction pour transcrire la parole"""
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Parlez maintenant...")
            r.adjust_for_ambient_noise(source, duration=1)
            audio_text = r.listen(source, timeout=10, phrase_time_limit=15)
            
        st.info("🔄 Transcription en cours...")
        text = r.recognize_google(audio_text, language=language_code)
        return text, True
        
    except sr.WaitTimeoutError:
        return "⏱️ Timeout : Aucune parole détectée.", False
    except sr.UnknownValueError:
        return "❌ Désolé, je n'ai pas pu comprendre ce qui a été dit.", False
    except sr.RequestError as e:
        return f"❌ Erreur du service de reconnaissance vocale : {e}", False
    except Exception as e:
        return f"❌ Erreur inattendue : {e}", False

def translate_text(text, source_lang_code, target_lang_code):
    """Fonction pour traduire le texte avec deep-translator"""
    try:
        translator = GoogleTranslator(source=source_lang_code, target=target_lang_code)
        translation = translator.translate(text)
        return translation, True
    except Exception as e:
        st.error(f"❌ Erreur de traduction : {e}")
        return None, False

def text_to_speech(text, language_code):
    """Fonction pour convertir le texte en parole dans la langue spécifiée"""
    try:
        # Utiliser gTTS pour générer l'audio dans la langue cible
        tts = gTTS(text=text, lang=language_code, slow=False)
        
        # Créer un fichier temporaire
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_filename = temp_file.name
        temp_file.close()
        
        # Sauvegarder l'audio
        tts.save(temp_filename)
        
        return temp_filename
    except Exception as e:
        st.error(f"❌ Erreur TTS : {e}")
        return None

def main():
    st.title("🎤 Traducteur Vocal Intelligent")
    st.markdown("---")
    
    # Interface utilisateur
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🗣️ Langue Source")
        source_lang = st.selectbox(
            "Langue que vous allez parler :",
            list(LANGUAGES.keys()),
            key="source_lang"
        )
        st.write(f"{LANGUAGES[source_lang]['flag']} {source_lang}")
    
    with col2:
        st.subheader("🌍 Langue Cible")
        available_targets = [lang for lang in LANGUAGES.keys() if lang != source_lang]
        target_lang = st.selectbox(
            "Langue de traduction :",
            available_targets,
            key="target_lang"
        )
        st.write(f"{LANGUAGES[target_lang]['flag']} {target_lang}")
    
    st.markdown("---")
    
    # Étape 1: Enregistrement
    st.subheader("📝 Étape 1: Enregistrement")
    
    if st.button("🎤 Commencer l'Enregistrement", key="record_btn"):
        recognition_code = LANGUAGES[source_lang]["recognition"]
        
        with st.spinner("🎤 Écoute en cours..."):
            text, success = transcribe_speech(recognition_code)
            
            if success:
                st.session_state['recorded_text'] = text
                st.session_state['source_lang_name'] = source_lang
                st.success("✅ Enregistrement réussi !")
            else:
                st.error(text)
                if 'recorded_text' in st.session_state:
                    del st.session_state['recorded_text']
    
    # Affichage du texte enregistré
    if 'recorded_text' in st.session_state:
        st.success(f"**Texte enregistré ({st.session_state['source_lang_name']}):**")
        st.write(f"📝 {st.session_state['recorded_text']}")
        
        st.markdown("---")
        
        # Étape 2: Traduction
        st.subheader("🔄 Étape 2: Traduction")
        
        if st.button("🔄 Traduire maintenant", key="translate_btn"):
            source_code = LANGUAGES[source_lang]["code"]
            target_code = LANGUAGES[target_lang]["code"]
            
            with st.spinner("🔄 Traduction en cours..."):
                translated_text, success = translate_text(
                    st.session_state['recorded_text'],
                    source_code,
                    target_code
                )
                
                if success and translated_text:
                    st.session_state['translated_text'] = translated_text
                    st.session_state['target_lang_name'] = target_lang
                    st.success("✅ Traduction terminée !")
                else:
                    st.error("❌ Échec de la traduction")
                    if 'translated_text' in st.session_state:
                        del st.session_state['translated_text']
        
        # Affichage de la traduction
        if 'translated_text' in st.session_state:
            st.success(f"**Traduction ({st.session_state['target_lang_name']}):**")
            st.write(f"🌍 {st.session_state['translated_text']}")
            
            st.markdown("---")
            
            # Étape 3: Écouter
            st.subheader("🔊 Étape 3: Écouter la traduction")
            
            if st.button("🔊 Écouter la Traduction", key="listen_btn"):
                with st.spinner("🔊 Génération de l'audio..."):
                    # Utiliser le code de langue pour la synthèse vocale
                    target_code = LANGUAGES[st.session_state['target_lang_name']]["code"]
                    audio_file = text_to_speech(st.session_state['translated_text'], target_code)
                    
                    if audio_file and os.path.exists(audio_file):
                        # Lire le fichier audio
                        with open(audio_file, 'rb') as f:
                            audio_data = f.read()
                        
                        st.audio(audio_data, format='audio/mp3')
                        st.success(f"🔊 Audio généré en {st.session_state['target_lang_name']} !")
                        
                        # Nettoyer le fichier temporaire
                        try:
                            os.unlink(audio_file)
                        except:
                            pass
                    else:
                        st.error("❌ Impossible de générer l'audio")
    
    st.markdown("---")
    
    # Boutons de contrôle
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Tout Effacer", key="clear_all"):
            keys_to_clear = ['recorded_text', 'translated_text', 'source_lang_name', 'target_lang_name']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("✅ Tout effacé !")
            st.rerun()
    
    with col2:
        if st.button("🔄 Nouvelle Traduction", key="new_translation"):
            if 'translated_text' in st.session_state:
                del st.session_state['translated_text']
            if 'target_lang_name' in st.session_state:
                del st.session_state['target_lang_name']
            st.success("✅ Prêt pour nouvelle traduction !")
            st.rerun()
    
    with col3:
        if st.button("🎤 Nouvel Enregistrement", key="new_recording"):
            keys_to_clear = ['recorded_text', 'translated_text', 'source_lang_name', 'target_lang_name']
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("✅ Prêt pour nouvel enregistrement !")
            st.rerun()
    
    # Informations
    with st.expander("ℹ️ Informations"):
        st.markdown("""
        ### 📋 Instructions d'utilisation :
        
        1. **Sélectionnez les langues** source et cible
        2. **Cliquez sur "Commencer l'Enregistrement"** et parlez clairement
        3. **Cliquez sur "Traduire maintenant"** pour obtenir la traduction
        4. **Cliquez sur "Écouter la Traduction"** pour entendre l'audio
        
        ### 🛠️ Langues disponibles :
        """)
        
        for lang_name, lang_info in LANGUAGES.items():
            st.write(f"- {lang_info['flag']} {lang_name}")
        
        st.markdown("""
        ### ⚠️ Dépendances requises :
        ```bash
        pip install streamlit speech-recognition deep-translator gtts pyaudio
        ```
        
        ### 🔧 Conseils :
        - Parlez clairement et distinctement
        - Assurez-vous d'avoir une bonne connexion Internet
        - Vérifiez que votre microphone fonctionne
        """)

if __name__ == "__main__":
    main()