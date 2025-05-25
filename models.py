import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    is_vip = Column(Boolean, default=False)
    free_analysis_used = Column(Boolean, default=False)
    vip_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_analysis = Column(DateTime, nullable=True)

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_telegram_id = Column(Integer, index=True)
    amount = Column(Integer)  # مبلغ به تومان
    authority = Column(String, unique=True)  # کد مرجع زرین‌پال
    status = Column(String, default="pending")  # pending, verified, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_telegram_id = Column(Integer, index=True)
    analysis_type = Column(String)  # free, vip
    analysis_data = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

# ایجاد جداول
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(telegram_id: int):
    """دریافت کاربر یا ایجاد کاربر جدید"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    finally:
        db.close()

def is_user_vip(telegram_id: int) -> bool:
    """بررسی VIP بودن کاربر"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            return False
        
        if user.is_vip and user.vip_expires:
            if user.vip_expires > datetime.utcnow():
                return True
            else:
                # انقضای اشتراک
                user.is_vip = False
                db.commit()
                return False
        return False
    finally:
        db.close()

def has_used_free_analysis(telegram_id: int) -> bool:
    """بررسی استفاده از تحلیل رایگان"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        return user.free_analysis_used if user else False
    finally:
        db.close()

def mark_free_analysis_used(telegram_id: int):
    """علامت‌گذاری استفاده از تحلیل رایگان"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            user.free_analysis_used = True
            user.last_analysis = datetime.utcnow()
            db.commit()
    finally:
        db.close()

def upgrade_to_vip(telegram_id: int):
    """ارتقاء کاربر به VIP"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            user.is_vip = True
            user.vip_expires = datetime.utcnow() + timedelta(days=30)
            db.commit()
    finally:
        db.close()

def save_analysis(telegram_id: int, analysis_type: str, analysis_data: str):
    """ذخیره تاریخچه تحلیل"""
    db = SessionLocal()
    try:
        analysis = AnalysisHistory(
            user_telegram_id=telegram_id,
            analysis_type=analysis_type,
            analysis_data=analysis_data
        )
        db.add(analysis)
        db.commit()
    finally:
        db.close()