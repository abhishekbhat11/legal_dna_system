# 🧬 CCMS Legal DNA Mapping System

An AI-powered document extraction engine built for the Centre for e-Governance. This system ingests Indian High Court judgments, semantically zones the text, and utilizes Google's Gemini 2.5 Flash model with strict Pydantic schemas to extract explicitly ordered directives ("Legal DNA").

It features a fast, split-screen React verification cockpit for human-in-the-loop validation before committing actions to a trusted dashboard.

## 🚀 Tech Stack
*   **Frontend:** React (Vite), Tailwind CSS v3, React Router v6, Axios, Lucide Icons.
*   **Backend:** Python 3.12+, FastAPI, Uvicorn, Google GenAI SDK (Native JSON), PyMuPDF (Fitz).
*   **AI Engine:** Google Gemini 2.5 Flash (via `google-genai` SDK).

---

## 🛠️ Prerequisites
Before running the project, ensure you have the following installed on your machine (or inside your WSL/Ubuntu environment):
*   [Node.js](https://nodejs.org/) (v18 or higher)
*   [Python](https://www.python.org/) (v3.12 or higher)
*   A **Google Gemini API Key** (Get one for free at [Google AI Studio](https://aistudio.google.com/))

---

## ⚙️ Installation & Setup (From Scratch)

After cloning the repository, you will need two separate terminal windows—one for the backend API and one for the React frontend.

### Part 1: Start the Python Backend

Open your first terminal and navigate to the backend folder:
```bash
cd backend
```

**1. Create a Virtual Environment**
To avoid system package conflicts, create an isolated Python environment:
```bash
python3 -m venv venv
```

**2. Activate the Environment**
*   **On Linux/Mac (or WSL):**
    ```bash
    source venv/bin/activate
    ```
*   **On Windows (PowerShell):**
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
*(You should now see `(venv)` at the start of your terminal prompt).*

**3. Install Dependencies**
Install the strict requirements for the API and Gemini SDK:
```bash
pip install fastapi uvicorn pydantic google-genai pymupdf python-multipart
```

**4. Add Your API Key**
Export your Gemini API key to the environment so the backend can securely access it:
*   **On Linux/Mac (or WSL):**
    ```bash
    export GEMINI_API_KEY="your-actual-api-key-here"
    ```
*   **On Windows (PowerShell):**
    ```powershell
    $env:GEMINI_API_KEY="your-actual-api-key-here"
    ```

**5. Boot the Server**
```bash
uvicorn main:app --reload
```
*The backend is now actively listening on `[http://127.0.0.1:8000](http://127.0.0.1:8000)`.*

---

### Part 2: Start the React Frontend

Open a **second terminal tab** and navigate to the frontend folder:
```bash
cd frontend
```

**1. Install Node Modules**
Install all UI dependencies (this handles the Tailwind CSS and React Router setups):
```bash
npm install
```

**2. Boot the Dev Server**
```bash
npm run dev
```

**3. Launch the App**
Click the local link provided in the terminal (usually `http://localhost:5173/`).

---

## 📁 Project Structure

```text
legal-dna-system/
├── backend/
│   ├── main.py              # FastAPI router and endpoints
│   ├── models.py            # Strict Pydantic schemas (SourceSpan, LegalGenome)
│   ├── pdf_processor.py     # PyMuPDF character span extraction
│   ├── zoning_engine.py     # Layer 1 Rule-based semantic classifier
│   └── llm_chain.py         # Google GenAI integration and prompt engineering
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VerificationCockpit.jsx  # Human-in-the-loop review UI
│   │   │   └── TrustedDashboard.jsx     # Post-verification data view
│   │   ├── App.jsx          # Main application wiring and state
│   │   └── index.css        # Tailwind directives
│   ├── tailwind.config.js   # UI styling configuration
│   └── package.json
└── dataset/                 # Put your test PDF judgments here
```

## ⚠️ Troubleshooting
*   **`externally-managed-environment` error during pip install:** This means you forgot to create or activate your virtual environment (`venv`). Follow Backend Step 1 & 2 carefully.
*   **`{"detail":"Not Found"}` when opening localhost:8000:** This is normal! The backend API does not have a homepage. You must interact with the system through the React frontend port (`5173`).
*   **Endless Loading Spinner in UI:** Ensure your `GEMINI_API_KEY` is exported in the exact terminal tab where you ran the `uvicorn` command. Check the backend terminal for specific error logs.
