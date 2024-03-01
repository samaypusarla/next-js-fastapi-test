from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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

# @app.post("/api/upload")
# async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     try:
#         print("Into uplaoding")
#         file_content = await file.read()  # Read file content
#         db_file = FileModel(filename=file.filename, content=file_content)
#         db.add(db_file)
#         db.commit()
#         db.refresh(db_file)
#         print("file is here:,", db_file.filename)
#         return {"filename": db_file.filename, "id": db_file.id}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/{file_id}")
async def get_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()    
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    return StreamingResponse(BytesIO(db_file.content), media_type="application/pdf")