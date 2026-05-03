from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pdf_processor import extract_text_with_spans
from zoning_engine import categorize_zones
from llm_chain import generate_legal_dna

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
        zoned_blocks = categorize_zones(blocks)
        
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