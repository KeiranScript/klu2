import os
import random
import string
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse

UPLOAD_DIR = "files"
MAX_UPLOAD_SIZE = 1024 * 1024 * 1024


def load_api_keys():
    if not os.path.exists('json/keys.json'):
        return {}
    with open('json/keys.json') as f:
        return json.load(f)


def save_api_keys(api_keys):
    with open('json/keys.json', 'w') as f:
        json.dump(api_keys, f, indent=4)


API_KEYS = load_api_keys()
app = FastAPI()


def generate_random_filename(extension: str) -> str:
    random_string = ''.join(random.choices(
        string.ascii_letters + string.digits, k=8))
    return f"{random_string}{extension}"


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if file.file._file.tell() > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400, detail="File size exceeds 1GB limit")

    extension = os.path.splitext(file.filename)[1]
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    random_filename = generate_random_filename(extension)
    file_path = os.path.join(UPLOAD_DIR, random_filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    file_url = f"http://localhost:6969/{random_filename}"
    return JSONResponse(content={"url": file_url})


@app.get("/{filename}")
async def serve_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)

    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=6969)
