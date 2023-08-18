import sqlalchemy
from typing import Union
from fastapi import BackgroundTasks, Depends, HTTPException

from app import app
from app.database import GetSessionDB, AsyncSession


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/create")
async def create_user(db: AsyncSession = Depends(get_db)):
    pass
