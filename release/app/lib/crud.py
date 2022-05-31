from sqlalchemy.orm import Session
from ..lib import models, schemas
from typing import Optional


"""
執行sql指令
"""
# 通過id查詢使用者
def get_all_user(db: Session):
    return db.query(models.User).all()

# 通過id查詢使用者
def get_user(db: Session, user_name: str):
    return db.query(models.User).filter(models.User.account == user_name).first()

# 通過id查詢管理員
def get_root_user(db: Session, user_name: str):
    return db.query(models.Root_User).filter(models.Root_User.account == user_name).first()

# 通過id查詢授權紀錄
def get_apply_record(db: Session, user_name: str, order_by: Optional[str] = 'DESC'):
    """
    order_by 默認降冪排序 DESC | ASC
    """
    if order_by == 'ASC':

        return  db.query(models.Apply_Token) \
                .filter(models.Apply_Token.account == user_name) \
                .order_by(models.Apply_Token.index.asc()).all()
    
    return  db.query(models.Apply_Token) \
            .filter(models.Apply_Token.account == user_name) \
            .order_by(models.Apply_Token.index.desc()).all()
    
    
# 新增使用者
def db_create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        account= user.account,
        hashed_password=user.hashed_password,
        email=user.email,
        company=user.company,
        phone=user.phone,
        name=user.name
        )
    db.add(db_user)
    db.commit()  # 提交儲存到資料庫中
    db.refresh(db_user)  # 重新整理
    return db_user


# 新增使用者
def db_create_token(db: Session, token: schemas.TokenRecord):
    db_token = models.Apply_Token(
        account = token.account,
        authorization_date = token.authorization_date,
        expiry_date = token.expiry_date,
        token = token.token,
        )
    db.add(db_token)
    db.commit()  # 提交儲存到資料庫中
    db.refresh(db_token)  # 重新整理
    return db_token


# 新增使用紀錄
def db_create_used_record(db: Session, used: schemas.UsedRecord):
    db_used = models.Used_Record(
        account = used.account,
        date = used.date,
        count = used.count,
        )
    db.add(db_used)
    db.commit()  # 提交儲存到資料庫中
    db.refresh(db_used)  # 重新整理
    return db_used