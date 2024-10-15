from fastapi import FastAPI, HTTPException, Depends
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional

from app.apis.deps import get_db
from app.db.db_models import ChatSession

"""
class ChatSession(DBaseModel):
    __tablename__ = 'chat_sessions'
    session_id = Column(Integer, unique=True, index=True)
    title = Column(String)
    messages = Column(JSON)
    right_sidebar_data = Column(JSON)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="chat_sessions", lazy="select")
"""
chat_history_router = APIRouter()


class Message(BaseModel):
    role: str
    content: str
    avatar: str
    round: int
    sessionId: int


class RightSidebarData(BaseModel):
    round: int
    type: str
    result: Optional[dict]


class ChatData(BaseModel):
    user_id: int
    session_id: int
    title: str
    messages: List[Message]
    right_sidebar_data: List[RightSidebarData]


@chat_history_router.post("/save_chat_data")
async def save_chat_data(chat_data: ChatData, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).filter(ChatSession.session_id == chat_data.session_id))
    db_chat_session = result.scalars().first()

    if db_chat_session:
        db_chat_session.title = chat_data.title
        db_chat_session.messages = chat_data.messages
        db_chat_session.right_sidebar_data = chat_data.right_sidebar_data
    else:
        db_chat_session = ChatSession(
            session_id=chat_data.session_id,
            user_id=chat_data.user_id,
            title=chat_data.title,
            messages=chat_data.messages,
            right_sidebar_data=chat_data.right_sidebar_data
        )
        db.add(db_chat_session)

    await db.commit()
    await db.refresh(db_chat_session)
    return {"message": "Chat data saved successfully"}


@chat_history_router.get("/get_chat_data")
async def get_chat_data(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).filter(ChatSession.session_id == session_id))
    db_chat_session = result.scalars().first()
    if db_chat_session is None:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return db_chat_session


@chat_history_router.get("/get_chat_history")
async def get_chat_history(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).order_by(ChatSession.create_at.desc()).limit(limit))
    chat_sessions = result.scalars().all()
    return chat_sessions
