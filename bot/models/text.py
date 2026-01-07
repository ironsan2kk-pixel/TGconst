"""Text model for content management."""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from bot.models.base import Base


class Text(Base):
    """Bot text content managed via admin panel."""
    
    __tablename__ = "texts"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(
        String(50),
        default="messages",
        nullable=False
    )  # messages, buttons, notifications
    text_ru: Mapped[str] = mapped_column(Text, nullable=False)
    text_en: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # Hint for admin
    variables: Mapped[str | None] = mapped_column(Text, nullable=True)  # Available vars
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def get_text(self, lang: str = "ru") -> str:
        """Get text by language."""
        return self.text_en if lang == "en" else self.text_ru
    
    def __repr__(self) -> str:
        return f"<Text(key={self.key!r}, category={self.category!r})>"
