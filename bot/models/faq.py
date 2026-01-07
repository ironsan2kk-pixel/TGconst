"""FAQ model."""

from sqlalchemy import Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from bot.models.base import Base, TimestampMixin


class FAQItem(Base, TimestampMixin):
    """FAQ question and answer."""
    
    __tablename__ = "faq_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_ru: Mapped[str] = mapped_column(Text, nullable=False)
    question_en: Mapped[str] = mapped_column(Text, nullable=False)
    answer_ru: Mapped[str] = mapped_column(Text, nullable=False)
    answer_en: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    def get_question(self, lang: str = "ru") -> str:
        """Get question by language."""
        return self.question_en if lang == "en" else self.question_ru
    
    def get_answer(self, lang: str = "ru") -> str:
        """Get answer by language."""
        return self.answer_en if lang == "en" else self.answer_ru
    
    def __repr__(self) -> str:
        return f"<FAQItem(id={self.id})>"
