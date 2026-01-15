from fastapi import FastAPI

app = FastAPI()

@app.post("/api/encode")
def encode():
    pass

@app.post("/api/decode")
def decode():
    pass
