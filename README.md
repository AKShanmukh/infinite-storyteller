# Infinite Storyteller Streamlit App

An interactive, AI-powered storytelling application built with Python and Streamlit. The application allows users to create accounts, sign in, generate custom stories based on prompts, select styles/genres, listen to stories read aloud, continue chapters dynamically, and download stories as PDF or TXT files.

## Features
- **User Authentication**: Secure signup and login flow powered by an SQLite database and SHA-256 password hashing.
- **AI Story Generation**: Custom story outline and content generation powered by OpenAI's `gpt-4o-mini` model.
- **Story Continuity**: Ability to append chapters to existing stories while maintaining plot and tone consistency.
- **Read Aloud (Text-to-Speech)**: Uses `pyttsx3` to generate vocal audio readouts of story chapters with selectable voice engines.
- **Export Options**: Prepare and download generated stories as formatted PDFs (via ReportLab) or standard TXT files.
- **Interactive History**: Tracks and lists the user's recent story generation prompts for easy retrieval.
- **Aesthetic UI**: Custom CSS and dark theme with blur overlays and background image bindings.

## Tech Stack
- **Streamlit** (Frontend Web Interface)
- **OpenAI Python SDK** (AI generation API)
- **SQLite3** (Local relational database)
- **pyttsx3** (Offline cross-platform text-to-speech)
- **ReportLab** (Dynamic PDF creation)
- **Python-dotenv** (Environment variable management)

## Setup Instructions

1. Clone or navigate to this folder.
2. Create a virtual environment and install the required dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up your API key in a `.env` file (see `.env.example`):
   ```env
   OPENAI_API_KEY=your-actual-api-key-here
   ```
4. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
