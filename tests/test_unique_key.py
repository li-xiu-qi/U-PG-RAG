# models.py

import bcrypt
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def get_current_time():
    from datetime import datetime
    return datetime.utcnow()


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

    @classmethod
    def get_unique_columns(cls):
        return [col.name for col in cls.__table__.columns if col.unique]


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

    @classmethod
    def get_unique_columns(cls):
        return [col.name for col in cls.__table__.columns if col.unique]


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)


def test_get_unique_columns():
    unique_columns = User.get_unique_columns()
    expected_columns = ['account', 'email', 'phone']

    if set(unique_columns) == set(expected_columns):
        print("Test passed!")
    else:
        print("Test failed!")
        print(f"Expected: {expected_columns}")
        print(f"Got: {unique_columns}")


if __name__ == "__main__":
    test_get_unique_columns()
