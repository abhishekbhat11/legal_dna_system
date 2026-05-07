import sqlite3
from pydantic import BaseModel

# Zero-config Hackathon Database
DB_NAME = "legaldna.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS verified_dna
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  action_subject TEXT, 
                  action_verb TEXT, 
                  timeline TEXT, 
                  strategy TEXT,
                  source_text TEXT)''')
    conn.commit()
    conn.close()

# Run immediately
init_db()

# Pydantic model for the incoming payload
class VerifiedDNA(BaseModel):
    action_subject: str
    action_verb: str
    timeline: str
    strategy: str
    source_text: str