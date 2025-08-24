import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String, nullable=True)
    phone_number = Column(String(20), unique=True, nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    full_name = Column(String(200), nullable=True)
    profile_picture = Column(String(500), nullable=True)
    
    # OAuth fields
    oauth_provider = Column(String(50), nullable=True)
    oauth_provider_id = Column(String(100), nullable=True)
    oauth_data = Column(Text, nullable=True)
    
    # 2FA Fields
    two_factor_secret = Column(String(255), nullable=True) # <-- ADD THIS LINE
    two_factor_enabled = Column(Boolean, default=False)   # <-- THIS LINE IS ALREADY THERE, ENSURE IT'S CORRECT

    # Verification fields
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    status = Column(String(50), default="pending_verification")
    token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)





    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, provider={self.oauth_provider})>"