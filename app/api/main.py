import sqlalchemy
from typing import Union
from fastapi import BackgroundTasks, Depends, HTTPException
from fastapi.responses import PlainTextResponse


from app import app
from .utils import OpenVPNConfigFile
# from .model import UserUsage, DetailsUsage
from app.database import get_db, AsyncSession


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/user/cretae")
async def create_user(db: AsyncSession = Depends(get_db)):
    pass


@app.post("/user/renew")
async def renew_user(db: AsyncSession = Depends(get_db)):
    pass
    # return FileResponse(path=file_path, filename=file_path, media_type='text/mp4')


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
    return OpenVPNConfigFile().text_response()
