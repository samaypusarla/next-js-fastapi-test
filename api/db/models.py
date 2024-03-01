from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, index=True)  # Store the user's prompt
    response = Column(Text, index=True)  # Store the AI's response
    created_at = Column(DateTime(timezone=True), server_default=func.now())
