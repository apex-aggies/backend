# Main API source
from fastapi import FastAPI
import scorer

app = FastAPI()
# Origin allow list for API calls
origins = [
    "http://localhost:4321",
    "http://127.0.0.1:4321",
    "http://localhost:80",
    "http://127.0.0.1:80",
    "https://secondlook.venykrid.com"
]

scorer = scorer.ComplianceScoringEngine 

@app.get("/")
async def root():
    return {"message": "Hello World"}
