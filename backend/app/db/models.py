from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reading_goal: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    library_items: Mapped[list["LibraryItem"]] = relationship("LibraryItem", back_populates="user")
    reviews: Mapped[list["BookReview"]] = relationship("BookReview", back_populates="user")


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    google_book_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    authors: Mapped[str] = mapped_column(String(256), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    cover_image: Mapped[str] = mapped_column(String(512), nullable=True)
    published_date: Mapped[str] = mapped_column(String(64), nullable=True)
    library_items: Mapped[list["LibraryItem"]] = relationship("LibraryItem", back_populates="book")
    reviews: Mapped[list["BookReview"]] = relationship("BookReview", back_populates="book")


class LibraryItem(Base):
    __tablename__ = "library_items"
    __table_args__ = (UniqueConstraint("user_id", "book_id", name="uq_library_user_book"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="General", nullable=False)
    reading_status: Mapped[str] = mapped_column(String(32), default="to_read", nullable=False)
    priority: Mapped[str] = mapped_column(String(32), default="medium", nullable=False)
    source: Mapped[str] = mapped_column(String(64), default="manual", nullable=False)
    reading_format: Mapped[str] = mapped_column(String(32), default="paper", nullable=False)
    pages_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pages_read: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[str | None] = mapped_column(Date, nullable=True)
    finished_at: Mapped[str | None] = mapped_column(Date, nullable=True)
    last_opened_at: Mapped[str | None] = mapped_column(Date, nullable=True)
    personal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship("User", back_populates="library_items")
    book: Mapped[Book] = relationship("Book", back_populates="library_items")


class BookReview(Base):
    __tablename__ = "personal_book_reviews"
    __table_args__ = (UniqueConstraint("user_id", "book_id", name="uq_review_user_book"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship("User", back_populates="reviews")
    book: Mapped[Book] = relationship("Book", back_populates="reviews")
