import json
import os
import streamlit as st

def load_translations(language_code):
    """Loads the JSON file corresponding to the selected language."""
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    file_path = os.path.join(root_path, "locales", f"{language_code}.json")
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def init_language():
    """Initializes the language state in the user's session."""
    if 'lang' not in st.session_state:
        st.session_state['lang'] = 'pt' # Default language
        
    st.session_state['translations'] = load_translations(st.session_state['lang'])

def t(key):
    """Main translation function. Returns the text based on the key."""
    return st.session_state.get('translations', {}).get(key, key)

def switch_language(new_lang):
    """Changes the global application language."""
    st.session_state['lang'] = new_lang
    st.session_state['translations'] = load_translations(new_lang)