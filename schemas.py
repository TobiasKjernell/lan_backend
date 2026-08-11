from pydantic import BaseModel, Field, SecretStr, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)

class UserPublic(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str

class SettingsBase(BaseModel):  
    name: str = Field(min_length=3, max_length=50)
    lan_date: datetime | None = None
    image_file: str | None = None

class SettingsUpdate(SettingsBase):
    pass

class SettingsResponse(SettingsBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    lan_date: datetime | None = None
    image_file: str | None = None
    image_url: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str
    

    