import datetime
from pydantic import (
    BaseModel,
    FieldValidationInfo,
    ValidationError,
    field_validator,
)


class User(BaseModel):
    username: str
    password: str
    expire: int | datetime.datetime
    limit: int = Field(gt=-1, description="data_limit can be 0 or greater")
    max_clients: int | None = None


    @field_validator("expire", mode="before")
    @classmethod
    def username_valid(cls, v: int, info: FieldValidationInfo) -> datetime.datetime:
        print(type(v))
        if not isinstance(v, int):
            raise ValueError("Int")
        print("->", info.field_name)
        print(datetime.datetime.now() + datetime.timedelta(days=v))
        return datetime.datetime.now() + datetime.timedelta(days=v)
