
# AI Response Generator

An AI-powered customer support response generator built with React, FastAPI, Python, and Groq.

## Features

- AI-powered response generation
- Customer message intent detection
- Order tracking and payment issue classification
- Markdown-formatted responses
- Input validation and error handling
- React frontend connected to FastAPI backend

## Technologies Used

- Python
- FastAPI
- Groq API
- Pydantic
- React
- Vite
- JavaScript

## Project Structure

- `backend/` — FastAPI backend and AI integration
- `nodejson/` — React frontend
- `backend/app/services/` — AI analysis and response generation

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Achyuth166/groq-ai-response-generator.git
cd groq-ai-response-generator
```

### 2. Configure the backend

Create and activate a Python virtual environment, then install the dependencies:

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirement.txt
```

Create `backend/.env` and configure your credentials:

```dotenv
GROQ_API_KEY=your_actual_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Get an API key from https://console.groq.com/keys.

### 3. Run the backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload --port 8000
```

API documentation: http://127.0.0.1:8000/docs

### 4. Run the frontend

Open a second terminal:

```bash
cd nodejson
npm install
npm run dev
```

Open the local URL printed by Vite, usually http://localhost:5173.

## Security

Never commit your `.env` file or publish your API key. Keep credentials private.

## Author

Kodi Achyuth
