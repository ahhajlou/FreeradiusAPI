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
    value: datetime.datetime | str
    op: RadiusOperators | str = RadiusOperators[':=']

    @field_validator("attribute", mode="before")
    @classmethod
    def atrribute_from_db(cls, v: str):
        if not isinstance(v, (str, RadiusAttributeType)):
            raise ValueError("attribute should be either RadiusAttributeType or str.")
        if isinstance(v, str):
            return RadiusAttributeType(v)
        return v

    @model_validator(mode="after")
    def check_all(self):
        if self.attribute == RadiusAttributeType.password:
            self.value = RadiusAttributeType.password.value

        if self.attribute == RadiusAttributeType.expiration:
            if isinstance(self.value, datetime.datetime):
                self.value = self.value.strftime('%Y-%m-%d')
            else:
                self.value = datetime.datetime.strptime(self.value, '%Y-%m-%d')


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



class RasdCheckTest(BaseModel):
    username: str
    attribute: str
    op: str
    value: str

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: dict[str, Any] | None = None,
    ):
        print("hi")
        print(type(obj))
        obj = obj.to_dict()
        return cls.__pydantic_validator__.validate_python(
            obj, strict=strict, from_attributes=from_attributes, context=context
        )

