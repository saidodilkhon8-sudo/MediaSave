from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum


class Base(DeclarativeBase):
    pass


class Platform(str, enum.Enum):
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    YOUTUBE_SHORTS = "youtube_shorts"
    SNAPCHAT = "snapchat"
    LIKEE = "likee"
    PINTEREST = "pinterest"
    THREADS = "threads"
    UNKNOWN = "unknown"


class MediaType(str, enum.Enum):
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    CAROUSEL = "carousel"
    UNKNOWN = "unknown"


class DownloadStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="ru")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    downloads: Mapped[list["Download"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    settings: Mapped[list["UserSetting"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Download(Base):
    __tablename__ = "downloads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[Platform] = mapped_column(SQLEnum(Platform), nullable=False)
    media_type: Mapped[MediaType] = mapped_column(SQLEnum(MediaType), nullable=False)
    status: Mapped[DownloadStatus] = mapped_column(SQLEnum(DownloadStatus), default=DownloadStatus.PENDING, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration: Mapped[float | None] = mapped_column(nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    uploader: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="downloads")


class UserSetting(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="settings")
