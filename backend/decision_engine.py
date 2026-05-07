import chromadb
from datetime import datetime, timedelta
import os

# ==========================================
# SIGNAL B: The Precedent Vector Database
# ==========================================
print("📦 Initializing ChromaDB Precedent Memory...")
chroma_client = chromadb.PersistentClient(path="./ml_models/chroma_db")
precedent_collection = chroma_client.get_or_create_collection(name="legal_precedents")

def seed_mock_precedents():
    """Hackathon Hack: We need fake historical data to prove the DB works during the demo."""
    if precedent_collection.count() == 0:
        print("🌱 Seeding mock precedent data for the demo...")
        precedent_collection.add(
            documents=[
                "The State shall constitute a committee to oversee the implementation of the aggregator guidelines.",
                "The respondent is hereby directed to refund the penalty amount of Rs. 50,000/-.",
                "The authority acted in haste without affording a reasonable opportunity to the petitioner."
            ],
            metadatas=[
                {"case_name": "Ola vs State (2022)", "action_taken": "COMPLY", "success": "Yes"},
                {"case_name": "Rapido vs RTO (2023)", "action_taken": "APPEAL", "success": "Won on Appeal"},
                {"case_name": "Uber vs Transport Dept (2021)", "action_taken": "APPEAL", "success": "Lost"}
            ],
            ids=["prec_1", "prec_2", "prec_3"]
        )

# Run the seeder immediately when the file loads
seed_mock_precedents()

def get_precedent_signal(current_direction: str) -> str:
    """Searches the Vector DB for similar past directions."""
    results = precedent_collection.query(
        query_texts=[current_direction],
        n_results=1
    )
    
    if results['documents'] and len(results['documents'][0]) > 0:
        past_doc = results['documents'][0][0]
        metadata = results['metadatas'][0][0]
        return f"Historical Precedent Found: In '{metadata['case_name']}', a similar direction ('{past_doc}') was met with strategy: {metadata['action_taken']}."
    return "No direct historical precedent found in database."

# ==========================================
# SIGNAL C: The Timeline Rules Engine
# ==========================================
STATUTORY_LIMITS = {
    "writ appeal": 30,
    "special leave petition": 90,
    "review petition": 30,
    "default compliance": 30
}

def calculate_inferred_deadline(text: str, order_date_str: str = "2026-01-23") -> str:
    """Calculates a hard deadline based on legal keywords if no explicit date is given."""
    text_lower = text.lower()
    days_to_add = STATUTORY_LIMITS["default compliance"] # Default fallback
    
    # Simple rule-based keyword matching
    if "writ appeal" in text_lower:
        days_to_add = STATUTORY_LIMITS["writ appeal"]
    elif "special leave petition" in text_lower or "slp" in text_lower:
        days_to_add = STATUTORY_LIMITS["special leave petition"]
    elif "review petition" in text_lower:
        days_to_add = STATUTORY_LIMITS["review petition"]
        
    # Calculate the exact date
    try:
        base_date = datetime.strptime(order_date_str, "%Y-%m-%d")
        deadline = base_date + timedelta(days=days_to_add)
        return f"Inferred Deadline: {deadline.strftime('%Y-%m-%d')} ({days_to_add} days statutory limit)"
    except Exception:
        return "Could not infer deadline."