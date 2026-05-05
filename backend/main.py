from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pdf_processor import extract_text_with_spans
from zoning_engine import zone_document
from llm_chain import generate_legal_dna
from database import VerifiedDNA, DB_NAME
import sqlite3

app = FastAPI(title="CCMS Legal DNA API")

# Allow the React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process-judgment")
async def process_judgment(file: UploadFile = File(...)):
    try:
        pdf_bytes = await file.read()
        
        # Layer 1: Ingestion & Zoning
        blocks = extract_text_with_spans(pdf_bytes)
        zoned_blocks = zone_document(blocks)
        
        # Layers 2, 3, 4: Legal DNA Extraction
        legal_genome = generate_legal_dna(zoned_blocks)
        
        return {
            "status": "success",
            "genome": legal_genome.model_dump(),
            "zoned_text": zoned_blocks 
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


@app.post("/api/save-dna")
async def save_dna(dna: VerifiedDNA):
    """Saves the verified DNA from the Review Cockpit to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO verified_dna (action_subject, action_verb, timeline, strategy, source_text) VALUES (?, ?, ?, ?, ?)",
              (dna.action_subject, dna.action_verb, dna.timeline, dna.strategy, dna.source_text))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Saved to Mission Control!"}

@app.get("/api/dashboard-stats")
async def get_dashboard_stats():
    """Fetches aggregated data for the React Recharts dashboard."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get counts of strategies per department (action_subject)
    c.execute("""
        SELECT action_subject, strategy, COUNT(*) 
        FROM verified_dna 
        GROUP BY action_subject, strategy
    """)
    rows = c.fetchall()
    conn.close()
    
    # Format data for Recharts: [{name: "Respondent No.1", COMPLY: 2, APPEAL: 1}, ...]
    dashboard_data = {}
    for row in rows:
        subject, strategy, count = row
        if subject not in dashboard_data:
            dashboard_data[subject] = {"name": subject, "COMPLY": 0, "APPEAL": 0}
        
        # Clean up the strategy string in case Gemini added extra text
        if "COMPLY" in strategy.upper():
            dashboard_data[subject]["COMPLY"] += count
        elif "APPEAL" in strategy.upper():
            dashboard_data[subject]["APPEAL"] += count

    return list(dashboard_data.values())