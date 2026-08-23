# Voice Command Shopping Assistant

This is a voice-controlled shopping list management web application. It features a minimalist interface, smart suggestions based on history and seasonality, and complete voice interaction.

## Approach & Tech Stack

Our approach focuses on maximum portability, minimal external dependencies, and premium user experience:

- **Frontend**: Pure HTML, Vanilla CSS, and JavaScript. We use the **Web Speech API** natively built into browsers (like Chrome/Edge) to perform speech-to-text directly on the client. This natively supports multiple languages and streaming without requiring paid AI API keys or heavy real-time streaming overhead over websockets.
- **Backend/Logic**: A lightweight **Python (Flask)** server handles the textual intents via REST API endpoints. The Python logic engine uses carefully crafted heuristic String and Regex matching (`nlp_parser.py`) to flawlessly interpret natural language variations like *"Add 2 bottles of water"*, categorize items dynamically (Produce, Dairy, etc.), and enforce logic for adding, removing, or searching.
- **Design System**: A responsive "Glassmorphism" UI optimized strictly for mobile and desktop, utilizing subtle CSS micro-animations to give live feedback when the microphone is listening. This ensures a clean, non-cluttered, voice-first semantic interface.

*(Total word count: ~153 words)*

## Running the Application Locally

1. Setup a virtual environment (optional) and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python app.py
   ```
3. Open `http://127.0.0.1:5000` in Google Chrome or Microsoft Edge.
4. Click the Microphone icon and grant permission to begin speaking! Try:
   - "Add 2 bottles of milk"
   - "Delete milk"
   - "Find organic apples under 5 dollars"
