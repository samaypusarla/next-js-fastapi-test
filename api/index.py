from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

from sqlalchemy.orm import Session

from api.db.database import engine, Base 

from api.db import models, schemas, database


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