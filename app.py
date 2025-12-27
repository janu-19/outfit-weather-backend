from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import outfit, travel, wardrobe

app = FastAPI(title="AI Outfit & Weather Assistant")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(outfit.router)
app.include_router(travel.router)
app.include_router(wardrobe.router)

@app.get("/")
def root():
    return {"status": "API running"}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
