from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
import base64
from io import BytesIO
import os
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware
import baseten
import numpy as np

BASE64_PREAMBLE = "data:image/png;base64,"
model = baseten.deployed_model_id('placeholder') #add baseten model id for Img2Img pipeline with nitrosocke/Ghibli-Diffusion model

app = FastAPI()

UPLOAD_FOLDER = os.path.abspath("initial_photos")
app.mount("/initial_photos", StaticFiles(directory=UPLOAD_FOLDER), name="initial_photos")

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
)

def b64_to_pil(b64_str):
    return Image.open(BytesIO(base64.b64decode(b64_str.replace(BASE64_PREAMBLE, ""))))

@app.get("/")
async def home():
    return {"message": "hello!"}

@app.post("/upload_photo")
async def upload_photo(file: UploadFile = File("test")):
    try:
        with open(os.path.join(UPLOAD_FOLDER, file.filename), "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        image = Image.open(filepath)

        image_bytes_io = BytesIO()
        image.save(image_bytes_io, format=image.format)
        image_bytes = image_bytes_io.getvalue()
        base64_encoded = base64.b64encode(image_bytes).decode("utf-8")  

        input = {
            "prompt" : "Ghibli style",
            "image" : base64_encoded
        }

        result = model.predict(input)

        b64_result = result.get("images")[0]
        result_image = b64_to_pil(b64_result) 
        result_image.save(filepath)
        
        return JSONResponse(content={"message": "Photo uploaded successfully", "result": b64_result}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": "Error uploading photo"}, status_code=500)

@app.get("/get_photo/{photo_name}")
async def get_photo(photo_name: str):
    photo_path = os.path.join(UPLOAD_FOLDER, photo_name)
    if os.path.exists(photo_path):
        return FileResponse(photo_path)
    return JSONResponse(content={"message": "Photo not found"}, status_code=404)
