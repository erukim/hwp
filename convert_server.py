import os
import uuid
import subprocess
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

TEMP_DIR = "/tmp/convert"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/convert")
async def convert(
    file: UploadFile = File(...),
    output_format: str = Form("docx")
):
    if output_format not in ["docx", "pdf", "odt"]:
        raise HTTPException(400, "Unsupported output format")

    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename)[1]
    input_path = os.path.join(TEMP_DIR, f"{file_id}{ext}")

    with open(input_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        subprocess.run([
            "libreoffice", "--headless", "--convert-to", output_format,
            "--outdir", TEMP_DIR, input_path
        ], check=True, timeout=30)

        output_path = os.path.join(TEMP_DIR, f"{file_id}.{output_format}")

        if not os.path.exists(output_path):
            raise HTTPException(500, "Conversion failed")

        return FileResponse(
            output_path,
            filename=f"{os.path.splitext(file.filename)[0]}.{output_format}",
            media_type="application/octet-stream",
            background=None
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "Conversion timeout")
    except subprocess.CalledProcessError:
        raise HTTPException(500, "Conversion error")
    finally:
        if os.path.exists(input_path):
            os.unlink(input_path)
