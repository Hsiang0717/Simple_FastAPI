from pydantic import BaseModel
from datetime import datetime 

'''
pydantic 資料格式,用來與router交互
pydantic 型別 
https://pydantic-docs.helpmanual.io/usage/types/
'''

class UserBase(BaseModel):
    """
    使用者基本資料格式：
    account:
    """
    account: str

class User(UserBase):
    """
    查詢帳號：
    account:
    email:
    phone:
    company:
    is_active
    並且設定orm_mode與之相容
    """
    email: str
    phone : str
    company : str
    name : str
    is_active: bool
    class Config:
        orm_mode = True

class UserCreate(UserBase):
    """
    建立帳號：
    account:
    hashed_password:
    email:
    company:
    phone:
    """
    hashed_password: str
    email: str
    company : str
    phone : str
    name : str

class UsedRecord(UserBase):
    """
    使用紀錄：
    account:
    date:
    count:
    """
    date : datetime
    count : int
    class Config:
        orm_mode = True

class TokenRecord(UserBase):
    """
    申請紀錄：
    account:
    authorization_date:
    expiry_date:
    token:
    並且設定orm_mode與之相容
    """
    authorization_date: datetime
    expiry_date : datetime
    token : str
    class Config:
        orm_mode = True