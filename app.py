# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "requests",
# ]
# ///

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Corrected list syntax
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Fixed missing commas
    allow_headers=["*"]
)

@app.get("/")
def home():
    return {"message": "TDS Project is difficult."}  # Optional: Use a clearer response key

if __name__ == "__main__":  # Fixed syntax
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Corrected `uvicorn.run`
