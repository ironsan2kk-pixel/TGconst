"""MenuItem model for menu constructor."""

from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class MenuItem(Base, TimestampMixin):
    """Menu item for bot menu constructor."""
    
    __tablename__ = "menu_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # section/link/text/faq/system
    system_action: Mapped[str | None] = mapped_column(String(50), nullable=True)  # tariffs/subscriptions/language/support/promocode
    text_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    text_en: Mapped[str] = mapped_column(String(100), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(10), nullable=True)  # Emoji
    value: Mapped[str | None] = mapped_column(Text, nullable=True)  # URL / message text / faq_id
    visibility: Mapped[str] = mapped_column(String(20), default="all", nullable=False)  # all/subscribed/not_subscribed
    visibility_language: Mapped[str] = mapped_column(String(10), default="all", nullable=False)  # all/ru/en
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Self-referential relationship for nested menus
    children: Mapped[list["MenuItem"]] = relationship(
        "MenuItem",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    parent: Mapped["MenuItem"] = relationship(
        "MenuItem",
        back_populates="children",
        remote_side=[id]
    )
    
    def get_text(self, language: str = "ru") -> str:
        """Get text based on language."""
        return self.text_en if language == "en" else self.text_ru
    
    def get_button_text(self, language: str = "ru") -> str:
        """Get button text with icon."""
        text = self.get_text(language)
        if self.icon:
            return f"{self.icon} {text}"
        return text
    
    def __repr__(self) -> str:
        return f"<MenuItem(id={self.id}, type={self.type!r}, text_ru={self.text_ru!r})>"
