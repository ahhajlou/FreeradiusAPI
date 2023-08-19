import sqlalchemy
from typing import Union
from fastapi import BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse


from app import app
from .utils import OpenVPNConfigFile
from .model import User, UserCreateResponse
from app.database import get_db, AsyncSession, GetSessionDB
from app.database.model import *
from app.database.query import create_user_db, get_user_db


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/user/create")#, response_model=UserCreateResponse)
async def create_user(user: User, db: AsyncSession = Depends(get_db)):
    try:
        await create_user_db(user, db)
    except sqlalchemy.exc.IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User exists.")
    # return user
    return {"msg": "hi"}

@app.post("/user/renew")
async def renew_user(db: AsyncSession = Depends(get_db)):
    pass
    # return FileResponse(path=file_path, filename=file_path, media_type='text/mp4')


@app.get("/user/{username}/get")
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    await get_user_db(username, db)



@app.get("/stats/{username}/overall")#, response_model=UserUsage)
async def overall_stats(username: str, db: AsyncSession = Depends(get_db)):
    pass


@app.get("/stats/{username}/details")#, response_model=DetailsUsage)
async def details_stats(username: str, db: AsyncSession = Depends(get_db)):
    pass


@app.get("/gets")
async def fie():
    return OpenVPNConfigFile().stream_response()


@app.get("/gett", response_class=PlainTextResponse)
async def fie():
    await GetSessionDB.create_all()
    return OpenVPNConfigFile().text_response()
