from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from ..lib import crud, schemas, utils

#router 初始化
router = APIRouter()


#html
templates = Jinja2Templates(directory="app/templates")

# 新建使用者
@router.post("/manage/create/", tags=["root"])
async def create_user(
    account:str,
    password:str,
    email:str,
    company:str,
    phone:str,
    name:str,
    db: Session = Depends(utils.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
    ):
    """
    新增使用者帳號、密碼、信箱、公司、電話
    """
    root_user = utils.authenticate_root_user(db, form_data.username, form_data.password)
    if not root_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user =  schemas.UserCreate(
        account = account,
        hashed_password = utils.get_password_hash(password),
        email = email,
        company = company,
        phone = phone,
        name = name,
    )

    if not user:
        raise HTTPException(status_code=404, detail="Check the empty colunm")

    return crud.db_create_user(db=db, user=user)


# 通過帳號查詢使用者
@router.get("/manage/{user_id}", response_model=schemas.User, tags=["root"])
async def read_user(user_id: str, db: Session = Depends(utils.get_db)):
    db_user = crud.get_user(db, user_name=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#建立使用者token
@router.post("/manage/token/", response_model=utils.Token, tags=["root"])
async def login_for_access_token(
        user_id: str, 
        date_time: datetime, 
        db: Session = Depends(utils.get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
        ):
    """
    get_user資料庫取得使用者並驗證->
    timedelta建立到期日->create_access_token建立token
    """
    root_user = utils.authenticate_root_user(db, form_data.username, form_data.password)
    if not root_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db_user = crud.get_user(db, user_name=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user_apply = crud.get_apply_record(db, user_name=user_id)

    """
    判斷是否有授權紀錄 
    有 -> 驗證是否到期 否 -> error 是 -> 建立token
    無 -> 建立token
    """

    if not db_user_apply:
        token = utils.create_new_token(db, db_user=db_user, date_time=date_time)
    else:
        if db_user_apply[0].expiry_date > datetime.now():
            raise HTTPException(status_code=404, detail="The last apply token is not expiry")
        else:
            token = utils.create_new_token(db, db_user=db_user, date_time=date_time)

    return token

# #建立使用者token 需要帳號密碼
# @router.post("/manage/token{user_account}", response_model=Token, tags=["root"])
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(utils.get_db)):
#     """
#     authenticate_user資料庫取得使用者並驗證->verify_password密碼驗證
#     timedelta建立到期日->create_access_token建立token
#     """
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     user_account = schemas.UserBase(account = user.account)
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"name": user_account}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}


@router.get("/login", tags=["test"])
async def login(request: Request):

    return templates.TemplateResponse("login.html", context= {"request": request})


@router.post("/index", tags=["test"])
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(utils.get_db)):
    user = utils.authenticate_root_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return templates.TemplateResponse("index.html", context= {"request": request})


@router.get("/tables", response_class=HTMLResponse, tags=["test"])
async def recipe(request: Request, db: Session = Depends(utils.get_db)):

    
    
    USERS = utils.object_as_dict(crud.get_all_user(db))
    

    return templates.TemplateResponse("tables.html", context= {"request": request, "recipe":USERS})