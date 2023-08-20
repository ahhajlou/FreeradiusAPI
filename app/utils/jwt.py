from jose import JWTError, jwt
from datetime import datetime, timedelta

# import sqlalchemy
# from app import app
from config import JWT_ALGORITHM, JWT_SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRE_MINUTES



# global JWT_SECRET_KEY


# @app.on_event("startup")
# def set_jwt_secret_key():
#     from app.db import JWT, engine, GetDB, get_jwt_secret_key
#     if sqlalchemy.inspect(engine).has_table(JWT.__tablename__):
#         with GetDB() as db:
#             global JWT_SECRET_KEY
#             JWT_SECRET_KEY = get_jwt_secret_key(db)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    data = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return data


