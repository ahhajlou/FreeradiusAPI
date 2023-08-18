import enum
from enum import Enum
from pydantic import BaseModel, field_validator, FieldValidationInfo, model_validator

from app.api.model import User

RadiusOperators = enum.Enum(
    "RadiusOperators", {
        "==": "==",
        ":=": ":=",
        "=": "="
    }
)


class PasswordType(str, Enum):
    clear_text = "Cleartext-Password"
    nt = "NT-Password"
    md5 = "MD5-Password"
    sha1 = "SHA1-Password"
    crypt = "Crypt-Password"


class RadiusAttribute(BaseModel):
    password: PasswordType = PasswordType.clear_text


class RadCheckModel(BaseModel):
    user: User
    attribute: RadiusAttribute
    op: RadiusOperators = RadiusOperators['==']
    value: str | None = None


    @field_validator("value", mode="before")
    @classmethod
    def value_(cls, v: str, info: FieldValidationInfo):
        if info.data['attribute'] == RadiusAttribute.password:
            return info.data['user'].password
        return v

    @model_validator(mode='after')
    def validated_radius(self):
        if self.attribute == RadiusAttribute.password:
            self.value = self.user.password
        return self
