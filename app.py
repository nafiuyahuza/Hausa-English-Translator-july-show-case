import gradio as gr
import pandas as pd
import difflib
import speech_recognition as sr

# Load your translations CSV
df = pd.read_csv("translations.csv")

# Function to handle voice input and translate
def transcribe_and_translate(audio_path, direction):
    if audio_path is None:
        return "❌ Please record something first."

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            user_input = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "❌ Could not understand the audio."
        except sr.RequestError:
            return "❌ Could not connect to Google API."

    return translate_text(user_input, direction, raw_input=user_input)

# Function for text translation
def translate_text(user_input, direction, raw_input=None):
    source_col = "english" if direction == "English to Hausa" else "hausa"
    target_col = "hausa" if direction == "English to Hausa" else "english"

    all_words = df[source_col].dropna().str.lower().tolist()
    match = difflib.get_close_matches(user_input.lower().strip(), all_words, n=1, cutoff=0.6)

    if match:
        result = df[df[source_col].str.lower() == match[0]][target_col].values[0]
        if raw_input:
            return f"🎧 You said: {raw_input}\n📝 Translation: {result}"
        else:
            return f"📝 Translation: {result}"
    else:
        if raw_input:
            return f"🎧 You said: {raw_input}\n❌ No translation found."
        else:
            return "❌ No translation found."

# Text translation tab
text_translator = gr.Interface(
    fn=translate_text,
    inputs=[
        gr.Textbox(label="Enter text"),
        gr.Radio(["English to Hausa", "Hausa to English"], label="Translation Direction")
    ],
    outputs="text",
    title="🗣️ Hausa–English Translator (Text)",
    description="Type a word or phrase to translate between English and Hausa.",
    flagging_mode="never",
    examples=[
        ["hello", "English to Hausa"],
        ["na gode", "Hausa to English"]
    ]
)

# Voice translation tab
voice_translator = gr.Interface(
    fn=transcribe_and_translate,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="🎤 Speak now"),
        gr.Radio(["English to Hausa", "Hausa to English"], label="Translation Direction")
    ],
    outputs="text",
    title="🎤 Hausa–English Voice Translator",
    description="Use your microphone to speak and translate with Google Speech Recognition.",
    flagging_mode="never"
)

# Combine both tabs
app = gr.TabbedInterface([text_translator, voice_translator], ["Text Translator", "Voice Translator"])

# Launch the app
app.launch(debug=True)

