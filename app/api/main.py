from fastapi import FastAPI


app = FastAPI(title="S3 Crypt Vault API")


@app.get("/health")
def health():
    return {"status": "ok"}