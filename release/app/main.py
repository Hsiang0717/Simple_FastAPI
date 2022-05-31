from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi import Depends
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from .routers import function_users, function_manager
from .lib import utils

#關閉預設doc
app = FastAPI(docs_url=None, redoc_url=None, openapi_url = None)

    
#載入router
app.include_router(function_users.router)
app.include_router(function_manager.router)
#載入CSS、js
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/js", StaticFiles(directory="app/js"), name="js")


#自定義doc include_in_schema=False: 從doc中移除 
@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(utils.get_HTTPBasic_Auth)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(utils.get_HTTPBasic_Auth)):
    return get_openapi(title = "FastAPI", version="0.1.0", routes=app.routes)

