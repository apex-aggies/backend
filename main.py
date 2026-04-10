# Main API source
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from scorer import *

engine = ComplianceScoringEngine()

app = FastAPI(
    title="Resume Audit API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc"
)

# Origin allow list for API calls
origins = [
    "http://localhost:4321",
    "http://127.0.0.1:4321",
    "http://localhost:80",
    "http://127.0.0.1:80",
    "https://secondlook.venykrid.com"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models based on scorer.py safe_get paths ---

class DecisionPacket(BaseModel):
    final_recommendation: Optional[str] = "unknown"
    reason_codes: Optional[List[str]] = Field(default_factory=list)
    explanation_present: Optional[bool] = False
    documentation_present: Optional[bool] = False

class ApplicantData(BaseModel):
    resume_parse_confidence: Optional[float] = None
    missing_fields: Optional[List[str]] = Field(default_factory=list)
    data_completeness_score: Optional[float] = None

class KeywordAssessment(BaseModel):
    keyword_score: Optional[float] = None
    possible_proxy_terms_detected: Optional[bool] = False
    overreliance_risk: Optional[bool] = False
    semantic_match_available: Optional[bool] = False
    keyword_rules_transparent: Optional[bool] = True

class OversightFeatures(BaseModel):
    decision_observability_score: Optional[float] = None
    contradiction_flag: Optional[bool] = False
    insufficient_explanation_flag: Optional[bool] = False
    vendor_transparency_limited: Optional[bool] = False

class AuditPayload(BaseModel):
    packet_id: Optional[str] = "UNKNOWN_PACKET"
    applicant_id: Optional[str] = "UNKNOWN_APPLICANT"
    decision_packet: Optional[DecisionPacket] = Field(default_factory=DecisionPacket)
    applicant_data: Optional[ApplicantData] = Field(default_factory=ApplicantData)
    keyword_assessment: Optional[KeywordAssessment] = Field(default_factory=KeywordAssessment)
    oversight_features: Optional[OversightFeatures] = Field(default_factory=OversightFeatures)

@app.get("/api")
async def root():
    return {"message": "Hello World"}

@app.post("/api/audit", response_model=RiskEvaluationResult)
async def evaluate_resume_packet(payload: AuditPayload):
    """
    Receives an applicant packet from Astro, evaluates it through the scoring engine,
    and returns the risk evaluation result.
    """
    # Dump the model
    packet_dict = payload.model_dump()
    
    # Run the engine
    result = engine.evaluate_packet(packet_dict)
    
    # Return the dataclass directly; FastAPI will convert it to JSON
    return result