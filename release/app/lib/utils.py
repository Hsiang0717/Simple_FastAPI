from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from ..lib import crud, schemas
from ..lib.database import SessionLocal


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBasic()

#資料庫初始化，如果沒有庫或者表，會自動建立
# Base.metadata.create_all(bind=engine) 

#Token資料格式
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None



# Dependency 取得資料庫
def get_db():
    """
    每一個請求處理完畢後會關閉當前連線，不同的請求使用不同的連線
    :return:
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



#將sql回來的物件轉為dic
def object_as_dict(objs):
    arr=[]
    for obj in objs:
        arr.append({c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs})
    
    return arr


#獲取當前使用者
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("name")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, user_name=token_data.username)
    if user is None:
        raise credentials_exception
    return user

#獲取當已啟用的使用者
async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


#密碼驗證
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

#明文轉換hash
def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db, username: str, password: str):
    """
    從資料庫裡驗證一般使用者
    """
    user = crud.get_user(db, user_name=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def authenticate_root_user(db, username: str, password: str):
    """
    從資料庫裡驗證管理員
    """
    user = crud.get_root_user(db, user_name=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    建立token
    """
    to_encode = data.copy()
    authorization_date = datetime.now()
    expiry_date = authorization_date + expires_delta
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return authorization_date, expiry_date, encoded_jwt


def create_new_token(db, db_user, date_time: datetime):
    """
    取得授權用戶帳號->
    timedelta建立到期日->create_access_token建立token
    """
    user = schemas.UserBase(account = db_user.account)

    ACCESS_TOKEN_EXPIRE_MINUTES = date_time - datetime.now()
    access_token_expires = timedelta(days= ACCESS_TOKEN_EXPIRE_MINUTES.days, 
                                     seconds= ACCESS_TOKEN_EXPIRE_MINUTES.seconds,
                                     microseconds= ACCESS_TOKEN_EXPIRE_MINUTES.microseconds)
    authorization_date, expiry_date, access_token = create_access_token(
        data={"name": user.account}, expires_delta=access_token_expires
    )

    token_info = schemas.TokenRecord(
        account=user.account,
        authorization_date= authorization_date,
        expiry_date= expiry_date,
        token = access_token,
        )

    crud.db_create_token(db, token=token_info)

    return {"access_token": access_token, "token_type": "bearer"}

#doc登入驗證
def get_HTTPBasic_Auth(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    root_user = authenticate_root_user(db, credentials.username, credentials.password)
    if not root_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.username