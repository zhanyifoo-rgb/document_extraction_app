import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class Document(Base):
    __tablename__= "documents"

    id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
    )

    filename: Mapped[str] = mapped_column(String(255))

    document_type: Mapped[str] = mapped_column(String(20))

    status: Mapped[str] = mapped_column(
        String(20),
        default="needs_review",
    )

    extracted_data: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )