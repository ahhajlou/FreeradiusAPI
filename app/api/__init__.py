from app import app

from .main import *


@app.get("/", status_code=204)
def base():
    return



