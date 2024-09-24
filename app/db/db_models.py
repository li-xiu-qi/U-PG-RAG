import json
from datetime import timedelta
from typing import Set

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, UniqueConstraint, CheckConstraint
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.orm import class_mapper

from app.apis.db_config import Base
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
        if exclude_relationships is None:
            exclude_relationships = ["users"]
        # return [rel.key for rel in class_mapper(cls).relationships if rel.key not in exclude_relationships]
        return [rel.key for rel in class_mapper(cls).relationships]

    @classmethod
    def get_all_columns(cls):
        return [col.name for col in cls.__table__.columns]


class Partition(DBaseModel):
    __tablename__ = 'partitions'

    partition_name = Column(String, unique=True, index=True, nullable=False)

    users = relationship("User", back_populates="partition", lazy="select")
    rag_caches = relationship("RAGCache", back_populates="partition", lazy="select")
    files = relationship("File", back_populates="partition", lazy="select")
    markdowns = relationship("Markdown", back_populates="partition", lazy="select")
    documents = relationship("Document", back_populates="partition", lazy="select")
    vectors = relationship("Vector", back_populates="partition", lazy="select")
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

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', account='{self.account}')>"

    @classmethod
    def get_disallowed_columns(cls) -> Set[str]:
        return {"hashed_password"}


class File(DBaseModel):
    __tablename__ = 'files'

    file_name = Column(String, index=True)
    file_hash = Column(String, index=True)
    reference_count = Column(Integer, default=1)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)

    partition = relationship("Partition", back_populates="files", lazy="select")
    markdowns = relationship("Markdown", back_populates="file", lazy="select")
    documents = relationship("Document", back_populates="file", lazy="select")
    vectors = relationship("Vector", back_populates="file", lazy="select")

    __table_args__ = (
        UniqueConstraint('partition_id', 'file_hash', name='uq_partition_file_hash'),
    )

    def __repr__(self):
        return f"<File(id={self.id}, file_name='{self.file_name}')>"


class Markdown(DBaseModel):
    __tablename__ = 'markdowns'

    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    hash_key = Column(String, unique=True, index=True, nullable=False)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)

    partition = relationship("Partition", back_populates="markdowns", lazy="select")
    file = relationship("File", back_populates="markdowns", lazy="select")
    documents = relationship("Document", back_populates="markdown", lazy="select")
    vectors = relationship('Vector', back_populates="markdown", lazy="select")

    def __repr__(self):
        return f"<Markdown(id={self.id}, title='{self.title}', hash_key='{self.hash_key}')>"


class Document(DBaseModel):
    __tablename__ = 'documents'

    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    hash_key = Column(String, unique=True, index=True, nullable=False)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    md_id = Column(Integer, ForeignKey('markdowns.id'), nullable=True)

    partition = relationship("Partition", back_populates="documents", lazy="select")
    file = relationship("File", back_populates="documents", lazy="select")
    markdown = relationship("Markdown", back_populates="documents", lazy="select")
    vectors = relationship("Vector", back_populates="document", lazy="select")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', hash_key='{self.hash_key}')>"


class Vector(DBaseModel):
    __tablename__ = 'vectors'

    page_content = Column(Text, unique=True, nullable=False)
    vector = Column(VECTOR, nullable=False)
    category = Column(String, nullable=True)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    md_id = Column(Integer, ForeignKey('markdowns.id'))
    doc_id = Column(Integer, ForeignKey('documents.id'), nullable=True)

    partition = relationship("Partition", back_populates="vectors", lazy="select")
    file = relationship("File", back_populates="vectors", lazy="select")
    markdown = relationship("Markdown", back_populates="vectors", lazy="select")
    document = relationship("Document", back_populates="vectors", lazy="select")

    def __repr__(self):
        return f"<Vector(id={self.id}, query_or_chunk='{self.page_content}')>"


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
