from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "InvoiceFlow API is running"}