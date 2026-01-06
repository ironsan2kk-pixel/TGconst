"""FAQItem model for questions and answers."""

from sqlalchemy import Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class FAQItem(Base, TimestampMixin):
    """FAQ question and answer."""
    
    __tablename__ = "faq_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_ru: Mapped[str] = mapped_column(String(500), nullable=False)
    question_en: Mapped[str] = mapped_column(String(500), nullable=False)
    answer_ru: Mapped[str] = mapped_column(Text, nullable=False)
    answer_en: Mapped[str] = mapped_column(Text, nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("menu_items.id", ondelete="SET NULL"), nullable=True)  # Section menu item
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    def get_question(self, language: str = "ru") -> str:
        """Get question based on language."""
        return self.question_en if language == "en" else self.question_ru
    
    def get_answer(self, language: str = "ru") -> str:
        """Get answer based on language."""
        return self.answer_en if language == "en" else self.answer_ru
    
    def __repr__(self) -> str:
        return f"<FAQItem(id={self.id}, question_ru={self.question_ru[:50]!r}...)>"
