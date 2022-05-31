from sqlalchemy import Boolean, Column, Integer, String, DateTime
from ..lib.database import Base


'''
資料庫表單格式，用來對應database的資料端
'''

class User(Base):
    '''
    使用者基本資料
    '''
    __tablename__ = "users"
    account = Column(String(32), primary_key=True, index=True)
    hashed_password = Column(String(32))
    email = Column(String(32), unique=True, index=True)
    company = Column(String(32), index=True)
    phone = Column(Integer())
    name = Column(String(32))
    is_active = Column(Boolean, default=False)

class Root_User(Base):
    '''
    使用者基本資料
    '''
    __tablename__ = "root_users"
    account = Column(String(32), primary_key=True, index=True)
    hashed_password = Column(String(32))

class Apply_Token(Base):
    '''
    API授權紀錄
    '''
    __tablename__ = "apply_record"
    index = Column(Integer(), primary_key=True)
    account = Column(String(32), index=True)
    authorization_date = Column(DateTime())
    expiry_date = Column(DateTime())
    token = Column(String(100))


class Used_Record(Base):
    '''
    API使用紀錄
    '''
    __tablename__ = "used_record"
    index = Column(Integer(), primary_key=True)
    account = Column(String(32), index=True)
    date = Column(DateTime())
    count = Column(Integer())