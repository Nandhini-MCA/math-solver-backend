from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class RoleEnum(enum.Enum):
    user = "user"
    ai = "ai"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=True) # Mutable for OAuth Google users
    google_id = Column(String, unique=True, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    questions = relationship("Question", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")
    learning_history = relationship("LearningHistory", back_populates="user")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_text = Column(Text)
    image_url = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="questions")
    solutions = relationship("Solution", back_populates="question")

class Solution(Base):
    __tablename__ = "solutions"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    solution_text = Column(Text)
    ai_model_used = Column(String, default="gpt-4")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    question = relationship("Question", back_populates="solutions")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    message = Column(Text)
    role = Column(Enum(RoleEnum))
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")

class LearningHistory(Base):
    __tablename__ = "learning_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="learning_history")
    
class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    solution_id = Column(Integer, ForeignKey("solutions.id"))
    note_text = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    solution_id = Column(Integer, ForeignKey("solutions.id"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
