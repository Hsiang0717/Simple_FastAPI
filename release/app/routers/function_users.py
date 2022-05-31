from os.path import exists
import os
import shutil
from datetime import datetime

from fastapi import APIRouter
from fastapi import UploadFile, File
from fastapi import Depends, HTTPException

from sqlalchemy.orm import Session

from ..lib import crud, schemas, utils

router = APIRouter()

DATA_PATH = "upload_data"
CType = ["text/csv", "audio/wav", "image/jpeg"]

#處理單一檔案 file: UploadFile= File(...),
@router.post("/upload_file/", tags=["users"])
def create_upload_file( file: UploadFile= File(...),
                        current_user: schemas.User = Depends(utils.get_current_active_user), 
                        db: Session = Depends(utils.get_db)
                        ):
    """
    判斷格式
    寫入紀錄
    建立資料夾與檔案
    模型推理
    刪除檔案
    """
    
    if file.content_type not in CType:
        raise HTTPException(status_code=404, detail="media type error")

    used_info = schemas.UsedRecord(
        account=current_user.account,
        date= datetime.now(),
        count = 1,
        )
    crud.db_create_used_record(db, used=used_info)

    folder_path = os.path.join(DATA_PATH, current_user.account)
    file_path = os.path.join(folder_path, file.filename)
    if not exists(folder_path):
        os.mkdir(folder_path)
    with open(file_path, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    
    result = "do some thing function"
    os.remove(file_path)
    # os.rmdir(folder_path)
    return result

