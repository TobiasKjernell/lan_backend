from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime
from config import settings 

from datetime import datetime, UTC
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)    

class LanSettings(Base):    
    __tablename__ = "lan_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    lan_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), nullable=True)
    image_file: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)

    @property 
    def image_url(self) -> str | None:
        if self.image_file:
            return f"https://{settings.s3_bucket_name}.s3.{settings.s3_region}.amazonaws.com/background_pics/{self.image_file}"
        return None