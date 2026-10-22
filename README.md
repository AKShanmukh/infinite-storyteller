# Infinite Storyteller

A Streamlit web app that writes stories with an LLM. You pick a genre and style, give it a prompt, and it writes
the story. You can keep adding chapters that stay consistent with the plot, listen to it read aloud, and download
it as a PDF or text file.

Demo video: [media/demo.mp4](media/demo.mp4)

## Features

- Sign-up and login backed by SQLite, with each user's prompt history saved
- Story and chapter generation with OpenAI `gpt-4o-mini`; new chapters are given the earlier text so the plot and
  tone carry over
- Text-to-speech playback with `pyttsx3` (works offline)
- Export to PDF (ReportLab) or TXT
- Custom dark theme with CSS

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # then put your OPENAI_API_KEY in .env
streamlit run app.py
```

Tests: `pytest test_app.py`

## What I'd improve

Passwords are hashed with plain SHA-256. A real deployment should use a salted, slow hash such as bcrypt or argon2.
Story generation also blocks the UI, and streaming the response would make it feel much faster.
