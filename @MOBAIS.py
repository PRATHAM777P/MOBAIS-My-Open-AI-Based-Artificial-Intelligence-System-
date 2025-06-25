import os
import argparse
import logging
import speech_recognition as sr
import pyttsx3
import openai
from dotenv import load_dotenv
import time
import re
from pydub import AudioSegment
from pydub.playback import play
import requests
import sqlite3
import tkinter as tk
from tkinter import scrolledtext, simpledialog

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='mobais_history.log', filemode='a')

# --- Personality/Character Mode ---
CHARACTER_MODES = {
    'helpful': 'You are a helpful assistant.',
    'funny': 'You are a witty, funny assistant who likes to joke.',
    'sarcastic': 'You are a sarcastic assistant who responds with dry humor.',
    'motivational': 'You are a motivational coach who encourages the user.',
    'formal': 'You are a formal and polite assistant.'
}

# --- Wake Word & Language ---
DEFAULT_WAKE_WORD = "hey pratham"
DEFAULT_LANGUAGE = "en-US"

# --- OpenAI API Key ---
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# --- Weather API Key (OpenWeatherMap) ---
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# --- Web Search API Key (SerpAPI or Bing) ---
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY')

# --- Intent Patterns ---
INTENT_PATTERNS = {
    'set_alarm': re.compile(r'set (an )?alarm( for)? (?P<time>.+)', re.I),
    'weather': re.compile(r'(what\'s|what is) the weather( like)?( today)?', re.I),
    'open_app': re.compile(r'open (?P<app>.+)', re.I),
    'reminder': re.compile(r'(remind me to|set a reminder to) (?P<task>.+)', re.I),
    'search_web': re.compile(r'(search for|look up) (?P<query>.+)', re.I),
}

# --- SQLite for Reminders ---
def init_db():
    conn = sqlite3.connect('mobais_reminders.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reminders (id INTEGER PRIMARY KEY, task TEXT, time TEXT)''')
    conn.commit()
    conn.close()

def add_reminder(task, time):
    conn = sqlite3.connect('mobais_reminders.db')
    c = conn.cursor()
    c.execute('INSERT INTO reminders (task, time) VALUES (?, ?)', (task, time))
    conn.commit()
    conn.close()

def get_reminders():
    conn = sqlite3.connect('mobais_reminders.db')
    c = conn.cursor()
    c.execute('SELECT task, time FROM reminders')
    reminders = c.fetchall()
    conn.close()
    return reminders

# --- Helper Functions ---
def check_file_exists(filepath):
    if not os.path.isfile(filepath):
        logging.error(f"File not found: {filepath}")
        raise FileNotFoundError(f"File not found: {filepath}")

def speak(text, output_audio=None, language=DEFAULT_LANGUAGE):
    engine = pyttsx3.init()
    engine.say(text)
    if output_audio:
        engine.save_to_file(text, output_audio)
    engine.runAndWait()

def recognize_speech_from_mic(recognizer, mic, language=DEFAULT_LANGUAGE):
    with mic as source:
        logging.info("Listening for wake word...")
        audio = recognizer.listen(source)
    try:
        result = recognizer.recognize_google(audio, language=language)
        logging.info(f"Heard: {result}")
        return result.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        logging.error(f"Speech Recognition error: {e}")
        return ""

def nlp_understanding(prompt, character_mode, language=DEFAULT_LANGUAGE):
    system_prompt = CHARACTER_MODES.get(character_mode, CHARACTER_MODES['helpful'])
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return "Sorry, I couldn't process that."

def recognize_intent(text):
    for intent, pattern in INTENT_PATTERNS.items():
        match = pattern.search(text)
        if match:
            return intent, match.groupdict()
    return 'general', {}

def get_weather():
    # Stub: Integrate with OpenWeatherMap
    if not WEATHER_API_KEY:
        return "Weather API key not set."
    # Example: requests.get(f"https://api.openweathermap.org/data/2.5/weather?q=London&appid={WEATHER_API_KEY}")
    return "The weather is sunny and pleasant! (This is a mock response.)"

def search_web(query):
    # Stub: Integrate with SerpAPI or Bing
    if not SEARCH_API_KEY:
        return f"Search API key not set. Here is a mock result for: {query}"
    # Example: requests.get(f"https://serpapi.com/search?q={query}&api_key={SEARCH_API_KEY}")
    return f"Here are the search results for: {query} (This is a mock response.)"

def execute_intent(intent, params):
    if intent == 'set_alarm':
        # Placeholder: Implement alarm logic
        return f"Alarm set for {params.get('time', 'unknown time')}."
    elif intent == 'weather':
        return get_weather()
    elif intent == 'open_app':
        app = params.get('app', '')
        # Placeholder: Implement app opening logic
        return f"Opening {app}... (Not really, just a demo!)"
    elif intent == 'reminder':
        task = params.get('task', '')
        add_reminder(task, time.strftime('%Y-%m-%d %H:%M:%S'))
        return f"Reminder set: {task}"
    elif intent == 'search_web':
        query = params.get('query', '')
        return search_web(query)
    else:
        return None

# --- GUI (Tkinter) ---
class MOBAIS_GUI:
    def __init__(self, root, character_mode):
        self.root = root
        self.root.title("MOBAIS Assistant")
        self.character_mode = character_mode
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20, font=("Arial", 12))
        self.text_area.pack(padx=10, pady=10)
        self.entry = tk.Entry(root, width=50, font=("Arial", 12))
        self.entry.pack(padx=10, pady=5, side=tk.LEFT)
        self.entry.bind('<Return>', self.process_input)
        self.record_btn = tk.Button(root, text="🎤 Record", command=self.record_speech)
        self.record_btn.pack(padx=5, pady=5, side=tk.LEFT)
        self.text_area.insert(tk.END, f"MOBAIS ({character_mode}): Ready!\n")
        # Play pratham.wav and show Listening...
        try:
            check_file_exists("pratham.wav")
            result_audio = AudioSegment.from_wav("pratham.wav")
            play(result_audio)
            self.text_area.insert(tk.END, "Listening...\n")
        except Exception as e:
            self.text_area.insert(tk.END, f"Error playing pratham.wav: {e}\n")
    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input.strip():
            return
        self.text_area.insert(tk.END, f"You: {user_input}\n")
        speak(user_input)  # Text-to-speech before processing
        intent, params = recognize_intent(user_input)
        response = execute_intent(intent, params)
        if not response:
            response = nlp_understanding(user_input, self.character_mode)
        self.text_area.insert(tk.END, f"MOBAIS: {response}\n")
        self.entry.delete(0, tk.END)
        speak(response)
    def record_speech(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        self.text_area.insert(tk.END, "Listening...\n")
        with mic as source:
            audio = recognizer.listen(source)
        try:
            user_input = recognizer.recognize_google(audio)
            self.text_area.insert(tk.END, f"You (spoken): {user_input}\n")
            speak(user_input)  # TTS for spoken input
            intent, params = recognize_intent(user_input)
            response = execute_intent(intent, params)
            if not response:
                response = nlp_understanding(user_input, self.character_mode)
            self.text_area.insert(tk.END, f"MOBAIS: {response}\n")
            speak(response)
        except sr.UnknownValueError:
            self.text_area.insert(tk.END, "Could not understand audio.\n")
        except sr.RequestError as e:
            self.text_area.insert(tk.END, f"Speech Recognition error: {e}\n")

# --- Main CLI/Voice Loop ---
def main():
    parser = argparse.ArgumentParser(description="MOBAIS: Modular OpenAI-Based Assistant with Intelligent Speech")
    parser.add_argument('--character', type=str, default='helpful', choices=CHARACTER_MODES.keys(), help="Choose the assistant's personality.")
    parser.add_argument('--output-audio', type=str, default=None, help="Path to save the output speech WAV file.")
    parser.add_argument('--wake-word', type=str, default=DEFAULT_WAKE_WORD, help="Custom wake word.")
    parser.add_argument('--language', type=str, default=DEFAULT_LANGUAGE, help="Language code for speech recognition (e.g., en-US, hi-IN).")
    parser.add_argument('--gui', action='store_true', help="Launch GUI mode.")
    parser.add_argument('--text-input', action='store_true', help="Enable text input mode in CLI (text-to-speech-to-text).")
    args = parser.parse_args()

    if not OPENAI_API_KEY:
        print("OpenAI API key not set. Please set the OPENAI_API_KEY environment variable.")
        return

    init_db()

    if args.gui:
        root = tk.Tk()
        app = MOBAIS_GUI(root, args.character)
        root.mainloop()
        return

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    # Play pratham.wav and show Listening... on CLI startup
    try:
        check_file_exists("pratham.wav")
        result_audio = AudioSegment.from_wav("pratham.wav")
        play(result_audio)
        print("Listening...")
    except Exception as e:
        print(f"Error playing pratham.wav: {e}")

    if args.text_input:
        print(f"MOBAIS is running in {args.character} mode (Text Input). Type your message:")
        while True:
            user_input = input("You: ")
            if not user_input.strip():
                continue
            speak(user_input, language=args.language)  # TTS for text input
            intent, params = recognize_intent(user_input)
            response = execute_intent(intent, params)
            if not response:
                response = nlp_understanding(user_input, args.character, language=args.language)
            print(f"Assistant: {response}")
            speak(response, args.output_audio, language=args.language)
            logging.info(f"User: {user_input}\nAssistant: {response}")
    else:
        print(f"MOBAIS is running in {args.character} mode. Say '{args.wake_word}' to activate.")
        speak(f"Hello! I am your {args.character} assistant. Say '{args.wake_word}' to start.", language=args.language)
        while True:
            heard = recognize_speech_from_mic(recognizer, mic, language=args.language)
            if args.wake_word.lower() in heard:
                print("Wake word detected! Listening for your command...")
                speak("Yes? How can I help you?", language=args.language)
                with mic as source:
                    audio = recognizer.listen(source)
                try:
                    user_text = recognizer.recognize_google(audio, language=args.language)
                    print(f"You said: {user_text}")
                except sr.UnknownValueError:
                    speak("Sorry, I didn't catch that.", language=args.language)
                    continue
                except sr.RequestError as e:
                    speak(f"Speech Recognition error: {e}", language=args.language)
                    continue
                intent, params = recognize_intent(user_text)
                response = execute_intent(intent, params)
                if not response:
                    response = nlp_understanding(user_text, args.character, language=args.language)
                print(f"Assistant: {response}")
                speak(response, args.output_audio, language=args.language)
                logging.info(f"User: {user_text}\nAssistant: {response}")
            else:
                print("Waiting for wake word...")
            time.sleep(1)

if __name__ == '__main__':
    main()
    








