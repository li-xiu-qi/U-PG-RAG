import json
from datetime import timedelta

import bcrypt
from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint, CheckConstraint

from app.db.utils import get_current_time
from app.apis.db_config import Base


class Partition(Base):
    __tablename__ = 'partitions'

    id = Column(Integer, primary_key=True, index=True)
    partition_name = Column(String, unique=True, index=True, nullable=False)
    create_at = Column(DateTime(timezone=True), default=get_current_time)
    update_at = Column(DateTime(timezone=True), default=get_current_time, onupdate=get_current_time)
    users = relationship("User", back_populates="partition")
    rag_caches = relationship("RAGCache", back_populates="partition")
    files = relationship("File", back_populates="partition")
    markdowns = relationship("Markdown", back_populates="partition")
    documents = relationship("Document", back_populates="partition")
    vectors = relationship("Vector", back_populates="partition")
    conversations = relationship("Conversation", back_populates="partition")
    response_records = relationship("ResponseRecord", back_populates="partition")

    def __repr__(self):
        return f"<Partition(id={self.id}, partition_name='{self.partition_name}')>"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False)
    account = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    create_at = Column(DateTime(timezone=True), default=get_current_time)
    update_at = Column(DateTime(timezone=True), default=get_current_time, onupdate=get_current_time)
    email = Column(String(100), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    role = Column(String(20), default='user', nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)

    partition = relationship("Partition", back_populates="users")
    tokens = relationship("Token", back_populates="user")
    rag_caches = relationship("RAGCache", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    response_records = relationship("ResponseRecord", back_populates="user")

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', account='{self.account}')>"


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    create_at = Column(DateTime(timezone=True), default=get_current_time)
    update_at = Column(DateTime(timezone=True), default=get_current_time, onupdate=get_current_time)
    expires_in = Column(DateTime(timezone=True), default=lambda: get_current_time() + timedelta(days=30),
                        nullable=False)
    ip_address = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="tokens")

    def __repr__(self):
        return f"<Token(id={self.id}, token='{self.token}', expires_in='{self.expires_in}')>"


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    file_hash = Column(String, index=True)
    reference_count = Column(Integer, default=1)
    create_at = Column(DateTime(timezone=True), default=get_current_time)
    update_at = Column(DateTime(timezone=True), default=get_current_time, onupdate=get_current_time)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)

    partition = relationship("Partition", back_populates="files")
    markdowns = relationship("Markdown", back_populates="file")
    documents = relationship("Document", back_populates="file")
    vectors = relationship("Vector", back_populates="file")

    # 添加联合唯一约束
    __table_args__ = (
        UniqueConstraint('partition_id', 'file_hash', name='uq_partition_file_hash'),
        CheckConstraint('(partition_id IS NULL AND file_hash IS NOT NULL) OR (partition_id IS NOT NULL)',
                        name='ck_partition_file_hash')
    )

    def __repr__(self):
        return f"<File(id={self.id}, file_name='{self.file_name}')>"


class Markdown(Base):
    __tablename__ = 'markdowns'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    hash_key = Column(String, unique=True, index=True, nullable=False)
    create_at = Column(DateTime(timezone=True), default=get_current_time)
    update_at = Column(DateTime(timezone=True), default=get_current_time, onupdate=get_current_time)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)

    partition = relationship("Partition", back_populates="markdowns")
    file = relationship("File", back_populates="markdowns")
    documents = relationship("Document", back_populates="markdown")
    vectors = relationship('Vector', back_populates="markdown")

    def __repr__(self):
        return f"<Markdown(id={self.id}, title='{self.title}', hash_key='{self.hash_key}')>"


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    hash_key = Column(String, unique=True, index=True, nullable=False)
    create_at = Column(DateTime(timezone=True), default=get_current_time)
    update_at = Column(DateTime(timezone=True), default=get_current_time, onupdate=get_current_time)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    md_id = Column(Integer, ForeignKey('markdowns.id'), nullable=True)

    partition = relationship("Partition", back_populates="documents")
    file = relationship("File", back_populates="documents")
    markdown = relationship("Markdown", back_populates="documents")
    vectors = relationship("Vector", back_populates="document")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', hash_key='{self.hash_key}')>"


class Vector(Base):
    __tablename__ = 'vectors'

    id = Column(Integer, primary_key=True, index=True)
    query_or_chunk = Column(Text, unique=True, nullable=False)
    vector = Column(VECTOR, nullable=False)
    category = Column(String, nullable=True)
    create_at = Column(DateTime(timezone=True), default=get_current_time)
    update_at = Column(DateTime(timezone=True), default=get_current_time, onupdate=get_current_time)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    md_id = Column(Integer, ForeignKey('markdowns.id'))
    doc_id = Column(Integer, ForeignKey('documents.id'), nullable=True)

    partition = relationship("Partition", back_populates="vectors")
    file = relationship("File", back_populates="vectors")
    markdown = relationship("Markdown", back_populates="vectors")
    document = relationship("Document", back_populates="vectors")

    def __repr__(self):
        return f"<Vector(id={self.id}, query_or_chunk='{self.query_or_chunk}')>"


class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, index=True)
    messages = Column(JSON, nullable=False)
    create_at = Column(DateTime(timezone=True), default=get_current_time)
    update_at = Column(DateTime(timezone=True), default=get_current_time, onupdate=get_current_time)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    partition = relationship("Partition", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    response_records = relationship("ResponseRecord", back_populates="conversation")

    def __repr__(self):
        messages_str = json.dumps(self.messages, ensure_ascii=False, indent=2)
        return f"<Conversation(id={self.id}, messages={messages_str})>"


class ResponseRecord(Base):
    __tablename__ = 'response_records'

    id = Column(Integer, primary_key=True, index=True)
    input = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    create_at = Column(DateTime(timezone=True), default=get_current_time)
    update_at = Column(DateTime(timezone=True), default=get_current_time, onupdate=get_current_time)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    partition = relationship("Partition", back_populates="response_records")
    conversation = relationship("Conversation", back_populates="response_records")
    user = relationship("User", back_populates="response_records")

    def __repr__(self):
        return f"<ResponseRecord(id={self.id}, input='{self.input}', response='{self.response}')>"


class RAGCache(Base):
    __tablename__ = 'rag_caches'

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    create_at = Column(DateTime(timezone=True), default=get_current_time)
    update_at = Column(DateTime(timezone=True), default=get_current_time, onupdate=get_current_time)
    expires_in = Column(DateTime(timezone=True), default=lambda: get_current_time() + timedelta(days=7), nullable=False)
    is_valid = Column(Boolean, default=True)
    partition_id = Column(Integer, ForeignKey('partitions.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    partition = relationship("Partition", back_populates="rag_caches")
    user = relationship("User", back_populates="rag_caches")

    def __repr__(self):
        return f"<RAGCache(id={self.id}, query='{self.query}', expires_in='{self.expires_in}', is_valid={self.is_valid})>"
