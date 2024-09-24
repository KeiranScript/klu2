import os
import random
import string
import jinja2
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
import uvicorn

UPLOAD_DIR = "files"
MAX_UPLOAD_SIZE = 1024 * 1024 * 1024

app = FastAPI()

app.mount("/templates", StaticFiles(directory="templates"), name="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


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

    # Update with your domain
    file_url = f"https://host.kuuichi.xyz/{random_filename}"
    return JSONResponse(content={"url": file_url})


@app.get("/", response_class=HTMLResponse)
async def root():
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("index.html")
    rendered_template = template.render()
    return HTMLResponse(content=rendered_template)


@app.get("/{filename}")
async def serve_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)

    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
