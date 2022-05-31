from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./mydatabase.db" #SQlite
#SQLALCHEMY_DATABASE_URL = 'mariadb+mariadbconnector://account:password@IP/database'

# echo=True表示引擎將用repr()函式記錄所有語句及其引數列表到日誌
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, encoding='utf8', echo=True
)

# SQLAlchemy中，CRUD是通過會話進行管理的，所以需要先建立會話，
# 每一個SessionLocal例項就是一個數據庫session
# flush指傳送到資料庫語句到資料庫，但資料庫不一定執行寫入磁碟
# commit是指提交事務，將變更儲存到資料庫檔案中
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立基本對映類
Base = declarative_base()