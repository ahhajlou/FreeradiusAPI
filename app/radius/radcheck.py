import datetime
from enum import Enum, auto
from typing import Any, List, Iterable

from pydantic import (
    Field,
    BaseModel,
    model_validator,
    ValidationError,
    field_validator,
    FieldValidationInfo,
    AliasPath,
    AliasChoices
)

from app.api.model import User

RadiusOperators = Enum(
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


class RadiusAttributeType(Enum):
    password: PasswordType | str = PasswordType.clear_text
    expiration: str = "Expiration"
    simultaneous_use: str = "Simultaneous-Use"


class RadiusAttributePair(BaseModel):
    attribute: RadiusAttributeType
    value: str
    op: RadiusOperators | str = RadiusOperators[':=']

    @field_validator("attribute", mode="after")
    @classmethod
    def password_enum_to_str(cls, v: RadiusAttributeType):
        if v == RadiusAttributeType.password:
            return v.value

    @field_validator("value", mode="after")
    @classmethod
    def password_to_str(cls, v: str, info: FieldValidationInfo):
        print(info)
        if info.data['attribute'] == RadiusAttributeType.expiration:
            if isinstance(v, datetime.datetime):
                return v.strftime('%Y-%m-%d')
            else:
                return datetime.datetime.strptime(v, '%Y-%m-%d')

    @field_validator("op", mode="after")
    @classmethod
    def attribute_convertor(cls, v: RadiusOperators | str, info: FieldValidationInfo):
        if isinstance(v, str):
            return RadiusOperators(v)
        else:
            return v.value


class RadCheckModel(RadiusAttributePair):  # Entrypoint
    username: str

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        if not isinstance(self.user, User):
            raise ValueError("Can not dump value queried from database.")

        result = dict()
        result.update(
            username=self.username,
            attribute=self.attribute.value,
            op=self.op.value,
            value=self.value
        )
        return result


class GenerateRadCheckModels(BaseModel):
    user: User
    radchecks: List[RadCheckModel] = []

    def gen(self):
        self.radchecks.append(
            RadCheckModel(
                username=self.user.username,
                attribute=RadiusAttributeType.password,
                value=self.user.password
            )
        )
        self.radchecks.append(
            RadCheckModel(
                username=self.user.username,
                attribute=RadiusAttributeType.expiration,
                value=self.user.expire
            )
        )

        if self.user.limit > 0:
            self.radchecks.append(
                RadCheckModel(
                    username=self.user.username,
                    attribute=RadiusAttributeType.simultaneous_use,
                    value=self.user.limit
                )
            )

