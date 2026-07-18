from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, LargeBinary, ForeignKey, ForeignKeyConstraint, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())


class ThreadMetadata(Base):
    __tablename__ = "thread_metadata"

    thread_id = Column(String(255), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="New Chat")
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    __table_args__ = (
        Index("idx_created_at", "created_at"),
        Index("idx_updated_at", "updated_at"),
    )


class DocumentMetadata(Base):
    __tablename__ = "document_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(String(255), nullable=False)
    filename = Column(String(500), nullable=False)
    documents_count = Column(Integer, nullable=False, default=0)
    chunks_count = Column(Integer, nullable=False, default=0)
    uploaded_at = Column(DateTime, default=func.current_timestamp())

    __table_args__ = (
        ForeignKeyConstraint(
            ["thread_id"],
            ["thread_metadata.thread_id"],
            ondelete="CASCADE"
        ),
        Index("idx_thread_id", "thread_id"),
    )


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    thread_id = Column(String(255), primary_key=True)
    checkpoint_ns = Column(String(255), primary_key=True, default="")
    checkpoint_id = Column(String(255), primary_key=True)
    parent_checkpoint_id = Column(String(255), nullable=True)
    type = Column(String(128), nullable=True)
    checkpoint = Column(LargeBinary, nullable=False)
    meta = Column(LargeBinary, nullable=False)

    __table_args__ = (
        Index("idx_parent", "thread_id", "checkpoint_ns", "parent_checkpoint_id"),
    )


class CheckpointWrite(Base):
    __tablename__ = "checkpoint_writes"

    thread_id = Column(String(255), primary_key=True)
    checkpoint_ns = Column(String(255), primary_key=True, default="")
    checkpoint_id = Column(String(255), primary_key=True)
    task_id = Column(String(255), primary_key=True)
    idx = Column(Integer, primary_key=True)
    channel = Column(String(128), nullable=False)
    type = Column(String(128), nullable=True)
    value = Column(LargeBinary, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["thread_id", "checkpoint_ns", "checkpoint_id"],
            ["checkpoints.thread_id", "checkpoints.checkpoint_ns", "checkpoints.checkpoint_id"],
            ondelete="CASCADE"
        ),
    )
