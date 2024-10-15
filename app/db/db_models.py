import json
import uuid
from datetime import timedelta
from typing import Set
from fastapi import HTTPException
from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, UniqueConstraint, select
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from sqlalchemy.orm import class_mapper
from db_config import Base
from app.db.utils import get_current_time


class DBaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    create_at = Column(DateTime(timezone=True), default=get_current_time)
    update_at = Column(DateTime(timezone=True), default=get_current_time, onupdate=get_current_time)

    @classmethod
    def get_unique_columns(cls):
        return [col.name for col in cls.__table__.columns if col.unique]

    @classmethod
    def get_disallowed_columns(cls) -> Set[str]:
        return set()

    @classmethod
    def get_relationship(cls, exclude_relationships: list = None) -> list:
        return [rel.key for rel in class_mapper(cls).relationships]

    @classmethod
    def get_all_columns(cls):
        return [col.name for col in cls.__table__.columns]

    @staticmethod
    async def check_foreign_key_exists(db: AsyncSession, table, foreign_key_id):
        query = select(table).where(table.c.id == foreign_key_id)
        result = await db.execute(query)
        exists = result.scalar_one_or_none()
        if not exists:
            raise HTTPException(status_code=404, detail=f"{table.name} with ID {foreign_key_id} does not exist.")


class Partition(DBaseModel):
    __tablename__ = 'partitions'

    partition_name = Column(String, unique=True, index=True, nullable=False)

    users = relationship("User", back_populates="partition", lazy="select")
    rag_caches = relationship("RAGCache", back_populates="partition", lazy="select")
    files = relationship("File", back_populates="partition", lazy="select")
    documents = relationship("Document", back_populates="partition", lazy="select")
    chunks = relationship("Chunk", back_populates="partition", lazy="select")
    conversations = relationship("Conversation", back_populates="partition", lazy="select")
    response_records = relationship("ResponseRecord", back_populates="partition", lazy="select")

    def __repr__(self):
        return f"<Partition(id={self.id}, partition_name='{self.partition_name}')>"


class User(DBaseModel):
    __tablename__ = 'users'

    name = Column(String(50), index=True, nullable=False)
    account = Column(String(50), unique=True, index=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    role = Column(String(20), default='user', nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)

    partition = relationship("Partition", back_populates="users", lazy="select")
    rag_caches = relationship("RAGCache", back_populates="user", lazy="select")
    conversations = relationship("Conversation", back_populates="user", lazy="select")
    response_records = relationship("ResponseRecord", back_populates="user", lazy="select")
    chat_sessions = relationship("ChatSession", back_populates="user", lazy="select")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', account='{self.account}')>"

    @classmethod
    def get_disallowed_columns(cls) -> Set[str]:
        return {"hashed_password"}


class ChatSession(DBaseModel):
    __tablename__ = 'chat_sessions'
    session_id = Column(Integer, unique=True, index=True)
    title = Column(String)
    messages = Column(JSON)
    right_sidebar_data = Column(JSON)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="chat_sessions", lazy="select")


class File(DBaseModel):
    __tablename__ = 'files'

    file_name = Column(String, index=True)
    file_hash = Column(String, index=True, unique=True, nullable=False)
    file_size = Column(Integer, nullable=True)
    content_type = Column(String, nullable=True)
    reference_count = Column(Integer, default=1)
    is_convert = Column(Boolean, default=False)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)

    partition = relationship("Partition", back_populates="files", lazy="select")
    documents = relationship("Document", back_populates="file", lazy="select")
    chunks = relationship("Chunk", back_populates="file", lazy="select")

    __table_args__ = (
        UniqueConstraint('partition_id', 'file_hash', name='uq_partition_file_hash'),
    )

    def __repr__(self):
        return f"<File(id={self.id}, file_name='{self.file_name}')>"


class Image(DBaseModel):
    __tablename__ = 'images'
    image_name = Column(String, index=True)
    image_hash = Column(String, index=True, unique=True, nullable=False)
    image_size = Column(Integer, nullable=True)
    reference_count = Column(Integer, default=1)

    def __repr__(self):
        return f"<Image(id={self.id}, image_name='{self.image_name}')>"


class Document(DBaseModel):
    __tablename__ = 'documents'
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    is_convert = Column(Boolean, default=False)
    doc_metadata = Column(JSONB, nullable=True)
    hash_key = Column(String, unique=True, index=True, nullable=False)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)

    partition = relationship("Partition", back_populates="documents", lazy="select")
    file = relationship("File", back_populates="documents", lazy="select")
    chunks = relationship("Chunk", back_populates="document", lazy="select")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', hash_key='{self.hash_key}')>"


class Chunk(DBaseModel):
    __tablename__ = 'chunks'

    page_content = Column(Text, nullable=False)
    vector = Column(VECTOR, nullable=False)
    category = Column(String, nullable=True)
    is_convert = Column(Boolean, default=False)
    doc_metadata = Column(JSONB, nullable=True)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=True)

    partition = relationship("Partition", back_populates="chunks", lazy="select")
    file = relationship("File", back_populates="chunks", lazy="select")
    document = relationship("Document", back_populates="chunks", lazy="select")

    def __repr__(self):
        return f"<Chunk(id={self.id}, page_content='{self.page_content}')>"


class Conversation(DBaseModel):
    __tablename__ = 'conversations'

    messages = Column(JSON, nullable=False)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    partition = relationship("Partition", back_populates="conversations", lazy="select")
    user = relationship("User", back_populates="conversations", lazy="select")
    response_records = relationship("ResponseRecord", back_populates="conversation", lazy="select")

    def __repr__(self):
        messages_str = json.dumps(self.messages, ensure_ascii=False, indent=2)
        return f"<Conversation(id={self.id}, messages={messages_str})>"


class ResponseRecord(DBaseModel):
    __tablename__ = 'response_records'

    input = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    partition = relationship("Partition", back_populates="response_records", lazy="select")
    conversation = relationship("Conversation", back_populates="response_records", lazy="select")
    user = relationship("User", back_populates="response_records", lazy="select")

    def __repr__(self):
        return f"<ResponseRecord(id={self.id}, input='{self.input}', response='{self.response}')>"


class Message(DBaseModel):
    __tablename__ = 'messages'
    role = Column(String(50))
    content = Column(Text)
    avatar = Column(String(255))
    round = Column(Integer)
    session_id = Column(String, default=lambda: str(uuid.uuid4()))


class RightSidebarData(DBaseModel):
    __tablename__ = 'right_sidebar_data'
    round = Column(Integer)
    type = Column(String(50))
    result = Column(JSON)
    session_id = Column(String, default=lambda: str(uuid.uuid4()))


class RAGCache(DBaseModel):
    __tablename__ = 'rag_caches'

    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    expires_in = Column(DateTime(timezone=True), default=lambda: get_current_time() + timedelta(days=7), nullable=False)
    is_valid = Column(Boolean, default=False)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    partition = relationship("Partition", back_populates="rag_caches", lazy="select")
    user = relationship("User", back_populates="rag_caches", lazy="select")

    def __repr__(self):
        return f"<RAGCache(id={self.id}, query='{self.query}', expires_in='{self.expires_in}', is_valid={self.is_valid})>"
