from pydantic import BaseModel, Field
from typing import List, Optional

class ConfidenceScores(BaseModel):
    extraction_confidence: int = Field(description="1-100: How explicitly is this direction stated?")
    timeline_confidence: int = Field(description="1-100: Is the date explicit (high), inferred (medium), or missing (low)?")
    action_confidence: int = Field(description="1-100: Is the responsible entity clearly named?")

# NEW: Strictly define the Source Span instead of using a lazy 'dict'
class SourceSpan(BaseModel):
    start_char: int = Field(description="Starting character index")
    end_char: int = Field(description="Ending character index")
    exact_text: str = Field(description="The exact quote from the text")

# NEW: Strictly define the Case Metadata instead of using a lazy 'dict'
class CaseMetadata(BaseModel):
    case_title: str = Field(description="Case title or 'Unknown'")
    date: str = Field(description="Date of the judgment or 'Unknown'")
    parties_involved: str = Field(description="Parties involved or 'Unknown'")

class LegalDNAUnit(BaseModel):
    action_verb: str = Field(description="What must be done (e.g., comply, pay, produce)")
    action_subject: str = Field(description="Who must do it (which department/officer)")
    action_object: str = Field(description="What it applies to")
    timeline_explicit: Optional[str] = Field(description="Date mentioned in text")
    timeline_inferred: Optional[str] = Field(description="Deadline inferred from legal knowledge")
    compliance_vs_appeal: str = Field(description="MUST BE: 'COMPLY' or 'APPEAL'")
    reasoning: str = Field(description="Why appeal or comply based on court language")
    source_span: SourceSpan  # <-- Fixed here
    confidence: ConfidenceScores
    is_verified: bool = False

class LegalGenome(BaseModel):
    case_metadata: CaseMetadata  # <-- Fixed here
    directions: List[LegalDNAUnit]