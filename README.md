# MOBAIS-My-Open-AI-Based-Artificial-Intelligence-System-

MOBAIS is a modular, voice-activated and text-based AI assistant built with Python, OpenAI GPT-4, and modern speech technologies. It supports both CLI and GUI modes, customizable personalities, wake words, and intent recognition for smart task execution.

---

## Features
- 🎙️ **Voice Input**: Speak to your assistant using your microphone.
- 🧠 **NLP Understanding**: Uses OpenAI GPT-4 for natural language understanding.
- 🔊 **Voice Output**: Assistant responds with both text and speech (TTS).
- 🤖 **Character Mode**: Choose from helpful, funny, sarcastic, motivational, or formal personalities.
- 🗣️ **Custom Wake Word**: Activate the assistant with your chosen hotword (default: "Hey Pratham").
- 📌 **Intent Recognition**: Understands commands like "set alarm", "what’s the weather", "open app", "remind me", and "search for".
- 📅 **Task Execution**: Performs actions like reminders, weather info, and web search (API integration ready).
- 🖥️ **GUI Mode**: Desktop chat window with text and voice input.
- 📝 **Logging**: All interactions are logged to `mobais_history.log`.
- 🌐 **Multilingual**: Supports multiple languages for speech recognition and TTS.
- 🎵 **Startup Sound**: Plays `pratham.wav` on launch.

---

## Setup

### 1. Clone the Repository
```sh
git clone <your-repo-url>
cd "Python program's/@MOBAIS/"
```

### 2. Install Dependencies
```sh
pip install -r requirement.txt
pip install simpleaudio
```

### 3. Set Your OpenAI API Key
```sh
# On Windows
set OPENAI_API_KEY=your_openai_api_key_here
# On Linux/Mac
export OPENAI_API_KEY=your_openai_api_key_here
```

### 4. (Optional) Set Weather and Search API Keys
- For live weather: `set WEATHER_API_KEY=your_openweathermap_key`
- For web search: `set SEARCH_API_KEY=your_serpapi_or_bing_key`

### 5. Ensure `pratham.wav` is Present
Place your startup audio file (`pratham.wav`) in the project directory.

---

## Usage

### **CLI (Voice Mode)**
```sh
python @MOBAIS.py
```
- Plays `pratham.wav`, shows "Listening...", then waits for your wake word and question.

### **CLI (Text Input Mode)**
```sh
python @MOBAIS.py --text-input
```
- Type your message, assistant will read it aloud and respond in both text and speech.

### **GUI Mode**
```sh
python @MOBAIS.py --gui
```
- Desktop chat window. Type or use the 🎤 Record button for speech input.

### **Custom Options**
- `--character` (helpful, funny, sarcastic, motivational, formal)
- `--wake-word` (set your own hotword)
- `--language` (e.g., en-US, hi-IN)

---

## Project Structure

```
@MOBAIS.py         # Main assistant code
requirement.txt    # Python dependencies
pratham.wav        # Startup audio
README.md          # This file
```

---

## Customization & Extending
- Add your own startup sound by replacing `pratham.wav`.
- Integrate real APIs for weather and web search by adding your API keys.
- Expand intent patterns and actions in `@MOBAIS.py`.
- Add more personalities or languages as needed.

---

## License
MIT License

---

## Credits
- Built with [OpenAI](https://openai.com/), [pydub](https://github.com/jiaaro/pydub), [SpeechRecognition](https://pypi.org/project/SpeechRecognition/), and Python.
- Voice and audio features powered by your system's audio backend (FFmpeg or simpleaudio).

---

**Enjoy your modular AI assistant!**
