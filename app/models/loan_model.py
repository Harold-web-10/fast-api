from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    loan_date = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    return_date = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, server_default=text("'active'"), index=True)

    user = relationship("User", back_populates="loans")
    device = relationship("Device", back_populates="loans")
