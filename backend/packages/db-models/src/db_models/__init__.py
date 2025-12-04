import uuid
from enum import Enum

from sqlalchemy import (
    JSON,
    UUID,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    Text,
    func,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata


class Sentence(Base):
    __tablename__ = "sentences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    text: Mapped[str] = mapped_column(Text, unique=True, index=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Word(Base):
    __tablename__ = "words"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    text: Mapped[str] = mapped_column(Text, unique=True, index=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class WordLookup(Base):
    __tablename__ = "word_lookups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    sentence_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sentences.id"), nullable=True, index=True
    )
    word_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("words.id"), nullable=True, index=True
    )

    text: Mapped[str] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Article(Base):
    __tablename__ = "article"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    url: Mapped[str] = mapped_column(Text, nullable=True)

    raw_html: Mapped[str] = mapped_column(Text, nullable=True)
    clean_html: Mapped[str] = mapped_column(Text, nullable=True)

    language: Mapped[str] = mapped_column(Text, nullable=True)
    site_name: Mapped[str] = mapped_column(Text, nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[str] = mapped_column(Text, nullable=True)
    hostname: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    fingerprint: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RawArticle(Base):
    __tablename__ = "raw_article"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    url: Mapped[str] = mapped_column(Text, nullable=True)
    raw_html: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Mindmap(Base):
    __tablename__ = "mindmap"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(Text, nullable=True)
    data: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class DocumentProcessTask(Base):
    __tablename__ = "document_process_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(
            TaskStatus,
            name="task_status",
            create_constraint=True,
            native_enum=True,
        ),
        default=TaskStatus.PENDING,
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
