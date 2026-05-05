# 🧬 Legal DNA System - Verification Cockpit

An enterprise-grade, AI-powered system designed to ingest complex legal judgments (PDFs), extract critical directives ("Legal DNA"), and provide a unified dashboard for tracking compliance and appeal deadlines.

Built for maximum reliability and speed, this project features a containerized architecture, a fast Python/FastAPI backend, an interactive React frontend, and generative AI extraction powered by Google Gemini.

---

## 🚀 Key Features

*   **Automated Extraction Pipeline:** Upload dense legal PDFs and let the AI instantly extract action subjects, verbs, and explicit/inferred timelines.
*   **Verification Cockpit:** An interactive Review UI that flags directives as either "COMPLY" or "APPEAL" alongside AI-generated legal reasoning.
*   **Mission Control Dashboard:** A historical data visualizer (powered by Recharts) to track extracted directives over time and manage city/corporate compliance.
*   **Vector Memory:** Integrates ChromaDB for intelligent precedent memory.
*   **Production-Ready:** Fully deployable via Docker for cross-platform, platform-agnostic reliability.

---

## 🛠️ Tech Stack

*   **Frontend:** React (Vite), Tailwind CSS, Recharts, Lucide Icons
*   **Backend:** Python 3.12, FastAPI, Uvicorn, PyMuPDF (`fitz`)
*   **AI/ML Engine:** Google Gemini API (GenAI SDK), ChromaDB
*   **Database:** SQLite (Persistent Volume)
*   **Infrastructure:** Docker & Docker Compose

---

## 💻 Quick Start Guide (Recommended)

The easiest way to run the application is using Docker. This ensures all dependencies, Node versions, and Python environments are perfectly isolated.

### Prerequisites
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
*   A valid [Google Gemini API Key](https://aistudio.google.com/app/apikey).

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/abhishekbhat11/legal_dna_system.git](https://github.com/abhishekbhat11/legal_dna_system.git)
    cd legal_dna_system
    git checkout upgrade
    
```

2.  **Export your Gemini API Key:**
    *Linux/Mac/WSL:*
    ```bash
    export GEMINI_API_KEY="your_actual_api_key_here"
    
```
    *Windows (PowerShell):*
    ```powershell
    $env:GEMINI_API_KEY="your_actual_api_key_here"
    ```

3.  **Build and launch the containers:**
    ```bash
    docker-compose up --build
    ```

4.  **Access the application:**
    Open your web browser and navigate to **`http://localhost:5173`**

*(To stop the server, press `Ctrl + C` in your terminal).*

---

## ⚙️ Manual Setup (Developer Mode)

If you prefer to run the application locally without Docker, follow these steps using two separate terminal windows.

### Terminal 1: Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   
```
4. Set your API key and start the server:
   ```bash
   export GEMINI_API_KEY="your_actual_api_key_here"
   uvicorn main:app --reload
   
```

### Terminal 2: Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   
```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   
```
4. Open the localhost URL provided by Vite in your browser.

---

## ⚠️ Troubleshooting & API Rate Limits

If you encounter `503 UNAVAILABLE` (High Traffic) or `429 RESOURCE_EXHAUSTED` (Quota Exceeded) errors during extraction, the Google Gemini API is rate-limiting your key.

**How to bypass for demonstrations:**
If you need to demonstrate the UI but the live API is blocking you, a fallback mechanism is included in the codebase.
1. Open `backend/llm_chain.py`.
2. Locate the `extract_legal_dna()` function.
3. Replace the live Gemini API call with the pre-written `mock_data` JSON string to ensure a flawless presentation of the UI and Database pipeline.
