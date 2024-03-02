from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from io import BytesIO
from openai import OpenAI
from pydantic import BaseModel

from sqlalchemy.orm import Session

from api.db.database import engine, Base, get_db 
from api.db import models, schemas, database
from .db.models import File as FileModel


class PromptModel(BaseModel):
    prompt: str


models.Base.metadata.create_all(bind=engine)


PPLX_API_KEY = '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'

app = FastAPI()



def create_tables():
    Base.metadata.create_all(bind=engine)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Allows both localhost and 127.0.0.1
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)


client = OpenAI(api_key=PPLX_API_KEY, base_url="https://api.perplexity.ai")

@app.post("/api/python")
async def hello_world(prompt: PromptModel, db: Session = Depends(database.get_db)):
    messages = [{"role": "user", "content": prompt.prompt}]
    
    # Assuming `client` is your API client for the AI model
    response = client.chat.completions.create(
        model="mistral-7b-instruct",
        messages=messages,
        max_tokens=1000
    )

    ai_response_content = response.choices[0].message.content

    # Save the prompt and response to the database
    new_message = models.Message(prompt=prompt.prompt, response=ai_response_content)
    db.add(new_message)
    db.commit()

    return {"message": ai_response_content}

### UPLOAD STATIC PDF ###
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        print("Into uplaoding")
        file_content = await file.read()  # Read file content
        db_file = FileModel(filename=file.filename, content=file_content)
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        print("file is here:,", db_file.filename)
        return {"filename": db_file.filename, "id": db_file.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/{file_id}")
async def get_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()    
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return StreamingResponse(BytesIO(db_file.content), media_type="application/pdf")


from pdf2image import convert_from_bytes

### CONVERT PDF TO IMAGES ###
@app.post("/api/uploadv1")
async def convert_PDF_to_Images(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_content = await file.read()
        images = convert_from_bytes(file_content)
        image_ids = []
        for i, image in enumerate(images):
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='JPEG')
            db_image = models.ImageModel(filename=f"{file.filename}_page_{i+1}.jpg", content=img_byte_arr.getvalue())
            db.add(db_image)
            db.commit()
            db.refresh(db_image)
            image_ids.append(db_image.id)
        return {"image_ids": image_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/images/{image_id}")
async def get_image(image_id: int, db: Session = Depends(get_db)):
    db_image = db.query(models.ImageModel).filter(models.ImageModel.id == image_id).first()
    if db_image is None:
        raise HTTPException(status_code=404, detail="Image not found")
    return StreamingResponse(BytesIO(db_image.content), media_type="image/jpeg")


UPLOAD_DIR = "uploads"
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8000

### UPLOAD STATIC PDF USING WEBSOCKET ###

@app.websocket("/upload-doc")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        if data == "start_upload":
            await websocket.send_text("Upload started. Please send the file.")
            file_content = await websocket.receive_bytes()            
            unique_filename = f"{websocket.client.host}_{websocket.client.port}_upload.pdf"
            file_path = f"{UPLOAD_DIR}/{unique_filename}"
            with open(file_path, "wb") as f:
                f.write(file_content)            
            file_url = f"http://{SERVER_HOST}:{SERVER_PORT}/{UPLOAD_DIR}/{unique_filename}"
            await websocket.send_text(f"File saved as: {file_url}")
        else:
            await websocket.send_text("Invalid command. Please send 'start_upload' to begin uploading.")
