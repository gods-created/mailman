from .base import Base 

from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, validates
from datetime import datetime

class Account(Base):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    smtp_server: Mapped[str] = mapped_column(String(150))
    smtp_account: Mapped[str] = mapped_column(String(150))
    smtp_password: Mapped[str] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now())

    @validates('smtp_password')
    def validate_smtp_password(self, key: str, value: str) -> str:
        from argon2 import PasswordHasher
        
        ph = PasswordHasher()
        password_hash = ph.hash(value)
        return password_hash

    __table_args__ = (
        Index('smtp_account_idx', 'smtp_account'),
    )

    def __repr__(self) -> str:
        return 'Account(smtp_server: str, smtp_account: str, smtp_password: str)'

    def __str__(self) -> str:
        return self.smtp_account

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'smtp_server': self.smtp_server,
            'smtp_account': self.smtp_account,
            'smtp_password': self.smtp_password,
            'created_at': self.created_at.strftime('%d.%m.%Y, %H:%M'),
        }